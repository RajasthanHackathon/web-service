import json

import googlemaps as googlemaps
import pyotp
import requests
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.views import View
from django.views.decorators.csrf import csrf_exempt, csrf_protect

import config
from bloodfinder.blood_rank import blood_rank
from bloodfinder.models import Request, PhoneNumber, Donor, SMSBuffer, BloodGroups, Donations

map_client = googlemaps.Client(key=config.key)

opt_key = "TMJHD4GPFOJQNKD3"

DONOR_HOTLINE = '9898'
USER_HOTLINE = '9999'

CLIENT_ID = "ad7288a4-7764-436d-a727-783a977f1fe1"

FAMILY_API = "apitest.sewadwaar.rajasthan.gov.in/app/live/Service/hofAndMember/ForApp/"  # /<Family_number>?clent_id=xxxx
'''
This API will provide the address of the user, either to register or to request blood.

We can also include blood group info to Bhamashah.

Family DNO can be used to regulate requests, allowing to filter out fraudulent requests.
'''

'''
Web Portal

Features:

* Registration
* Request Blood
'''


def portal_index(request):
    return render(request, "bloodfinder/web_index.html")


def portal_success(request):
    return render(request, 'bloodfinder/portal_sucess.html')


class PortalRequestBlood(View):
    def get(self, request):
        return render(request, 'bloodfinder/request.html', {
            'blood_groups': BloodGroups.CHOICES
        })

    def post(self, request):
        request_ = Request()
        if PhoneNumber.objects.filter(phone=request.POST['phone']).exists():
            phone = PhoneNumber.objects.get(phone=request.POST['phone'])
        else:
            phone = PhoneNumber(phone=request.POST['phone'])
            phone.save()
        request_.phone = phone
        request_.blood_group = request.POST['blood_group']
        request_.high_volume = 'high_volume' in request.POST
        request_.district = request.POST['pin_code']
        request_.save()
        return redirect('portal_success')


class PortalRegistrationPhoneVerify(View):
    def get(self, request):
        return render(request, 'bloodfinder/portal_registration.html', {
            'blood_groups': BloodGroups.CHOICES
        })

    def post(self, request):
        request.session['context'] = {'phone': request.POST['phone'], 'name': request.POST['name'],
                                      'district': request.POST['pin_code'],
                                      'blood_group': request.POST['blood_group']}
        sms = SMSBuffer()
        sms.sender = "BDF-VERIFY"
        sms.to = request.POST['phone']
        sms.message = "Your OTP is " + pyotp.TOTP(opt_key).now()
        print(sms.message)
        sms.save()
        return redirect('portal_donor_registration')


class PortalDonorRegistration(View):
    def get(self, request):
        return render(request, 'bloodfinder/portal_registration_otp.html')

    def post(self, request):
        otp = request.POST['otp']
        if pyotp.TOTP(opt_key).verify(otp, valid_window=300):
            context = request.session['context']
            donor = Donor()
            donor.phone = context['phone']
            donor.name = context['name']
            donor.pin_code = context['pin_code']
            donor.blood_group = context['blood_group']
            donor.save()
            del request.session['context']
        else:
            return render(request, 'bloodfinder/portal_registration_otp.html', {'error': 'Incorrect OTP'})
        return redirect('portal_success')


'''
Admin Views

Features:
* Update Donor Settings
* Registration
* Analytics
* Complaints

'''

'''
APIs

* Search
* Update
* Complaint
* Feedback

'''


@csrf_exempt
def api_search(request):
    request_ = Request()
    data = json.loads(request.body)
    print(data)
    if PhoneNumber.objects.filter(phone=data['phone']).exists():
        phone = PhoneNumber.objects.get(phone=data['phone'])
    else:
        phone = PhoneNumber(phone=data['phone'])
        phone.save()
    request_.phone = phone
    request_.blood_group = data['blood_group']
    request_.high_volume = data['high_volume']
    request_.district = data['pin_code']
    request_.save()
    donor_list = blood_rank(request_)
    for donor in donor_list:
        d = Donations()
        d.donor = donor
        d.request = request_
        d.save()
        sms = SMSBuffer()
        sms.sender = DONOR_HOTLINE
        sms.to = donor.phone
        sms.message = "There is a request for your blood urgently. Please confirm by replying to this SMS with a YES."
        sms.save()
        print(sms.message)

    return JsonResponse({'status': 'ok'})


@csrf_exempt
def api_donor_confirm(request):
    number = request.POST['number']
    donation = Donations.objects.get(has_accepted=None, donor__phone=number)
    donation.has_accepted = True
    donation.save()
    return JsonResponse({'status': 'ok'})


@csrf_exempt
def api_user_complete(request):
    number = request.POST['number']
    donations = Donations.objects.filter(has_accepted=True, request__phone__phone=number)
    for donation in donations:
        donation.has_completed = True
        donation.save()
    return JsonResponse({'status': 'ok'})


@csrf_exempt
def get_sms(request):
    num = request.GET['number']
    sms_list = SMSBuffer.objects.filter(to=num, is_sent=False)
    for sms in sms_list:
        print(sms)
        sms.is_sent = True
        sms.save()
    return JsonResponse({'message_list': [i.serialize for i in sms_list]})


# @csrf_exempt
# def api_donor_register(request):
#     number = request.POST['number']
#     family_dno = request.POST['family_no']
#     url = FAMILY_API + family_dno
#     r = requests.get(family_dno,params={'client_id':CLIENT_ID})
#     data = r.json()
#     donor = Donor()
#     donor.name = request.POST['name']
#     donor.family_id = family_dno
#     donor.

'''
Simulation
i) Dialer
'''

def dial(request):
    return render(request , 'bloodfinder/dialer.html');