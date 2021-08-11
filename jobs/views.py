from django.shortcuts import render

# Create your views here.
from django.views import generic

from .models import JobOffer, UserProfile, Company


class JobOffersView(generic.DetailView):
    model = JobOffer
    template_name = 'job_offers.html'


class UserProfileView(generic.DetailView):
    model = UserProfile
    template_name = 'user_profile.html'


class CompanyView(generic.DetailView):
    template_name = 'company_details.html'
    model = Company

