import googlemaps
import math
from django.db.models import Max, Count
from django.utils import timezone

import config
from bloodfinder.models import Donor, Request, BloodGroups, Donations
BLOOD_MATCH_COEFF = 1
DISTANCE_COEFFICIENT = 1
DONNATIONS_COEFF = 1

matrix_i = [BloodGroups.On, BloodGroups.Op, BloodGroups.Bn, BloodGroups.Bp, BloodGroups.An,
            BloodGroups.Ap, BloodGroups.ABn, BloodGroups.ABp]
matrix_j = matrix_i[::-1]

blood_match_matrix = [
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 1, 0, 1, 0, 1, 0],
    [1, 1, 0, 0, 1, 1, 0, 0],
    [1, 0, 0, 0, 1, 0, 0, 0],
    [1, 1, 1, 1, 0, 0, 0, 0],
    [1, 0, 1, 0, 0, 0, 0, 0],
    [1, 0, 0, 0, 0, 0, 0, 0],
]

map_client = googlemaps.Client(key=config.key)

class WeightedDonor:
    def __init__(self):
        self.donor = None
        self.weight = None


def get_blood_weight(target_group, current_group):
    if target_group == current_group:
        return 1
    i = matrix_i.index(target_group)
    j = matrix_j.index(current_group)
    if blood_match_matrix[i][j] == 1:
        return 0.75
    else:
        return 0


def get_weighted_donors(request: Request):
    district = request.pin_code
    blood_group = request.blood_group
    weighted_list = []
    max_donations = Donations.objects.values('donor').annotate(count=Count('donor')).aggregate(Max('count'))['count__max']
    if max_donations is None:
        max_donations = 0
    for d in Donor.objects.exclude(donations__request=request):
        w = WeightedDonor()
        w.donor = d
        w.weight = get_blood_weight(blood_group, d.blood_group)
        if w.weight == 0:
            continue
        if Donations.objects.filter(donor=d, request=request).exists():
            continue
        location = map_client.geocode(address=request.pin_code)
        lattitude = location[0]['geometry']['location']['lat']
        longitude = location[0]['geometry']['location']['lng']
        w.weight += math.sqrt(math.pow(longitude-float(d.longitude),2)+math.pow(lattitude-float(d.lattitude),2))
        if d.donations_set.filter(is_completed=True).exists():
            if d.donations_set.filter(is_completed=True).last().request.time - timezone.now() < timezone.timedelta(weeks=12):
                continue
            else:
                w.weight /= (d.donations_set.filter(is_completed=True).last().request.time - timezone.now()).days
        w.weight += float(Donations.objects.filter(donor=d).count())/float(max_donations+1)
        weighted_list.append(w)
    weighted_list.sort(key=(lambda x:x.weight))
    return weighted_list


def blood_rank(request: Request, top=3):
    weighted_list = get_weighted_donors(request)
    print(weighted_list)
    donor_list = [w.donor for w in weighted_list]
    return donor_list[:top]
