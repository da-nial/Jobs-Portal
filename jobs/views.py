from django.shortcuts import render

# Create your views here.
from django.views import generic

from .models import JobOffer


class JobOffersView(generic.DetailView):
    model = JobOffer
    template_name = 'job_offers.html'

