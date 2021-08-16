from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import generic
from .models import JobOffer, UserProfile, Company, EducationalBackground, Application
from .forms import EducationalBackgroundForm, SkillForm, EditProfileForm
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages


@login_required
def apply(request, pk):
    if request.method == 'POST':
        offer = get_object_or_404(JobOffer, pk=pk)
        if request.user.profile is None:
            messages.error(request, 'Complete your profile before application')
            return HttpResponseRedirect(reverse('jobs:job_offers', kwargs={'pk': pk}))
        elif request.user.has_pending_application_for_offer(offer):
            messages.error(request, 'Already applied for this offer')
            return HttpResponseRedirect(reverse('jobs:job_offers', kwargs={'pk': pk}))
        else:
            resume = request.FILES.get('resume')
            Application.objects.create(user=request.user, offer=offer, resume=resume)
            messages.success(request, 'Successfully applied for this offer')
            return HttpResponseRedirect(reverse('jobs:job_offers', kwargs={'pk': pk}))
    return Http404('Apply request only accepts "POST" method')


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
        messages.success(request, 'Successfully edited')
        return render(request, template_name, get_edit_profile_context_data(request))


def delete_skill(request, skill_id):
    user_profile = UserProfile.objects.get(user=request.user)
    user_profile.skills.remove(skill_id)
    return HttpResponseRedirect(reverse('jobs:edit_profile'))


def delete_educational_background(request, educational_background_id):
    EducationalBackground.objects.get(pk=educational_background_id).delete()
    return HttpResponseRedirect(reverse('jobs:edit_profile'))


class MainView(LoginRequiredMixin, generic.ListView):
    template_name = 'main.html'
    context_object_name = 'offers'
    login_url = settings.LOGIN_URL

    def get_queryset(self):
        return JobOffer.objects.all().order_by('pk')

    def get_context_data(self, **kwargs):
        context = super(MainView, self).get_context_data(**kwargs)
        context['companies'] = Company.objects.all().order_by('pk')
        return context
