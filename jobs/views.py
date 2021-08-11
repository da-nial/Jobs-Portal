from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from django.urls import reverse
from django.views import generic

from .models import JobOffer, UserProfile, Company, EducationalBackground
from .forms import EducationalBackgroundForm, SkillForm, EditProfileForm


class JobOffersView(generic.DetailView):
    model = JobOffer
    template_name = 'job_offers.html'


class UserProfileView(generic.DetailView):
    model = UserProfile
    template_name = 'user_profile.html'


class CompanyView(generic.DetailView):
    template_name = 'company_details.html'
    model = Company


def get_dictionary(query_dictionary, key):
    return query_dictionary if key in query_dictionary else None


def get_edit_profile_context_data(request):
    return {
        'edit_profile_form': EditProfileForm(data=get_dictionary(request.POST, 'edit'),
                                             instance=request.user.profile),
        'skill_form': SkillForm(data=get_dictionary(request.POST, 'add_skill')),
        'educational_background_form': EducationalBackgroundForm(
            data=get_dictionary(request.POST, 'add_educational_background'))
    }


@login_required
def edit_profile_view(request):
    template_name = 'edit_profile.html'
    if request.method == 'GET':
        return render(request, template_name, get_edit_profile_context_data(request))
    else:
        if 'edit' in request.POST:
            form = EditProfileForm(data=request.POST, instance=request.user.profile)
        elif 'add_skill' in request.POST:
            form = SkillForm(data=request.POST)
        elif 'add_educational_background' in request.POST:
            form = EducationalBackgroundForm(data=request.POST)
        else:
            return render(request, template_name, get_edit_profile_context_data(request))

        if not form.is_valid():
            return render(request, template_name, get_edit_profile_context_data(request))

        form.save_profile_form(request.user.profile)
        return render(request, template_name, get_edit_profile_context_data(request))


def delete_skill(request, skill_id):
    user_profile = UserProfile.objects.get(user=request.user)
    user_profile.skills.remove(skill_id)
    return HttpResponseRedirect(reverse('jobs:edit_profile'))


def delete_educational_background(request, educational_background_id):
    EducationalBackground.objects.get(pk=educational_background_id).delete()
    return HttpResponseRedirect(reverse('jobs:edit_profile'))
