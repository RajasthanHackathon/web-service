from django.shortcuts import render
from django.urls import path
from django.views.generic import TemplateView

from bloodfinder import views

urlpatterns = [
    path('', views.portal_index, name="portal_index"),
    path('register', views.PortalRegistrationPhoneVerify.as_view(), name="portal_registration_phone_verify"),
    path('register/verify', views.PortalDonorRegistration.as_view(), name="portal_donor_registration"),
    path('request', views.PortalRequestBlood.as_view(), name="portal_request_blood"),
    path('success', views.portal_success, name="portal_success"),

    path('api/request', views.api_search, name="api_search"),
    path('api/user/complete', views.api_user_complete, name="user_complete"),
    path('api/donor/confirm', views.api_donor_confirm, name="donor_confirm"),

    path('api/getsms', views.get_sms, name="get_sms"),

    path('simulate/dial' , views.dial , name="simulate_dial"),
    path('simulate/sms', TemplateView.as_view(template_name='bloodfinder/sms.html'), name="simulate_sms")

]