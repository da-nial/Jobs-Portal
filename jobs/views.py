from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import generic
from .models import JobOffer, UserProfile, Company, EducationalBackground, Application, AltEmail, Resume
from django.utils.translation import ugettext_lazy as _
from .resume_pdf_render import ResumePdfRender
from .forms import EducationalBackgroundForm, SkillForm, EditProfileForm, AltEmailForm, FilterJobOfferForm
from django.contrib import messages
from jobs.mail_service import send_verification_email
from django.views.decorators.http import require_http_methods
from django.core.files import File


@login_required
def apply(request, pk):
    if request.method == 'POST':
        offer = get_object_or_404(JobOffer, pk=pk)
        if request.user.profile is None:
            messages.error(request, _('Complete your profile before application'))
            return HttpResponseRedirect(reverse('jobs:job_offers', kwargs={'pk': pk}))
        elif not offer.is_enabled:
            messages.error(request, 'this job is disabled!')
            return HttpResponseRedirect(reverse('jobs:job_offers', kwargs={'pk': pk}))
        elif request.user.has_pending_application_for_offer(offer):
            messages.error(request, _('Already applied for this offer'))
            return HttpResponseRedirect(reverse('jobs:job_offers', kwargs={'pk': pk}))
        else:
            resume = request.FILES.get('resume')
            Application.objects.create(user=request.user, offer=offer, resume=resume)
            messages.success(request, _('Successfully applied for this offer'))
            return HttpResponseRedirect(reverse('jobs:job_offers', kwargs={'pk': pk}))
    return Http404(_('Apply request only accepts "POST" method'))


class JobOffersView(generic.DetailView):
    model = JobOffer
    template_name = 'job_offer.html'

    def get(self, request, *args, **kwargs):
        context = super().get(request, *args, **kwargs)
        user = request.user

        if user.is_authenticated and not user.has_requirement_for_offer(self.get_object()):
            messages.warning(request, _(
                "Based on your profile, You don't have not one of the skills,"
                " education or location requirements of this job opening."))
        return context


class UserProfileView(LoginRequiredMixin, generic.DetailView):
    def get_object(self, queryset=None):
        try:
            return self.request.user.profile
        except UserProfile.DoesNotExist:
            raise Http404()

    model = UserProfile
    template_name = 'user_profile.html'


class CompanyView(generic.DetailView):
    template_name = 'company_details.html'
    model = Company

    def get_context_data(self, **kwargs):
        context = super(CompanyView, self).get_context_data(**kwargs)
        job_offers = self.get_related_job_offers()
        context['page_obj'] = job_offers
        context['filter_job_offer'] = FilterJobOfferForm(data=self.request.GET)
        return context

    def get_related_job_offers(self):
        check_remove_filter(self.request)
        form = FilterJobOfferForm(data=self.request.GET)
        filter_context = {}
        if form.is_valid():
            filter_context = form.cleaned_data
        queryset = JobOffer.objects.filter_job(minimum_work_experience=filter_context['minimum_work_experience'],
                                               category=filter_context['category'],
                                               city=filter_context['city'],
                                               company=self.get_object()).order_by('pk')
        paginator = Paginator(queryset, 2)
        page = self.request.GET.get('page', 1)
        job_offers_in_page = paginator.get_page(page)
        return job_offers_in_page


def get_dictionary(query_dictionary, key):
    return query_dictionary if key in query_dictionary else None


def get_edit_profile_context_data(request):
    return {
        'edit_profile_form':
            EditProfileForm(data=get_dictionary(request.POST, 'edit'),
                            instance=request.user.profile),
        'skill_form':
            SkillForm(data=get_dictionary(request.POST, 'add_skill')),
        'educational_background_form':
            EducationalBackgroundForm(data=get_dictionary(request.POST,
                                                          'add_educational_background')),
        'alt_email_form': AltEmailForm(user_profile=None)
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
        messages.success(request, _('Successfully edited'))
        return render(request, template_name, get_edit_profile_context_data(request))


@login_required
def delete_skill(request, skill_id):
    Resume.delete_resume(request.user.profile)
    user_profile = UserProfile.objects.get(user=request.user)
    user_profile.skills.remove(skill_id)
    return HttpResponseRedirect(reverse('jobs:edit_profile'))


@login_required
def delete_educational_background(request, educational_background_id):
    Resume.delete_resume(request.user.profile)
    EducationalBackground.objects.get(pk=educational_background_id).delete()
    return HttpResponseRedirect(reverse('jobs:edit_profile'))


@login_required
@require_http_methods(['POST'])
def add_alt_email(request):
    user_profile = request.user.profile
    if user_profile is None:
        return HttpResponse("To add alternative emails, you have to create a profile first!")

    form = AltEmailForm(data=request.POST, user_profile=user_profile)

    if not form.is_valid():
        messages.error(request, form.errors)
        return HttpResponseRedirect(reverse('jobs:edit_profile'))

    form.save()
    messages.success(request, 'Email successfully added')
    return HttpResponseRedirect(reverse('jobs:edit_profile'))


@login_required
@require_http_methods(['POST'])
def delete_alt_email(request, alt_email_pk):
    user_profile = UserProfile.objects.get(user=request.user)
    try:
        alt_email = user_profile.alt_emails.get(pk=alt_email_pk)
        alt_email.delete()
        messages.success(request, f"Email {alt_email.address} deleted successfully")
    except AltEmail.DoesNotExist:
        messages.error(request, "No such email exists")

    return HttpResponseRedirect(reverse('jobs:edit_profile'))


@login_required
@require_http_methods(['POST'])
def send_email_verification(request, email_pk):
    alt_email = get_object_or_404(AltEmail, pk=email_pk)

    profile = request.user.profile
    if alt_email.user_profile != profile:  # Email is not for this user
        return HttpResponse('Invalid Email')

    alt_email.refresh_verification_token()

    send_verification_email(request, alt_email)
    messages.success(request, f"Verification email sent to {alt_email.address}")

    return HttpResponseRedirect(reverse("jobs:edit_profile"))


@login_required
def verify(request, token):
    try:
        email = AltEmail.objects.get(verification_token=token)

        email.verification_token = None
        email.is_verified = True
        email.save()
        messages.success(request, 'Thank you for your email confirmation.')
        return HttpResponseRedirect('/')

    except AltEmail.DoesNotExist:
        return HttpResponse('Verification link is invalid!')


def check_remove_filter(request):
    request.GET = request.GET.copy()
    if request.GET.get('remove_filter_minimumWork'):
        request.GET['minimum_work_experience'] = 0
    if request.GET.get('remove_filter_city'):
        request.GET['city'] = 'AL'
    if request.GET.get('remove_filter_category'):
        request.GET['category'] = 'AL'


class MainView(generic.ListView):
    template_name = 'main.html'
    context_object_name = 'offers'
    login_url = settings.LOGIN_URL
    paginate_by = 5

    def get_queryset(self):
        check_remove_filter(self.request)
        form = FilterJobOfferForm(data=self.request.GET)
        filter_context = {}
        if form.is_valid():
            filter_context = form.cleaned_data
        return JobOffer.enabled.get_queryset().filter_job(
            minimum_work_experience=filter_context['minimum_work_experience'],
            category=filter_context['category'],
            city=filter_context['city']).order_by('pk')

    def get_context_data(self, **kwargs):
        context = super(MainView, self).get_context_data(**kwargs)
        context['companies'] = Company.objects.all().order_by('pk')
        if self.request.user.is_authenticated and self.request.user.profile:
            context['appropriate_offers'] = JobOffer.enabled.appropriate_offers_for_profile(
                self.request.user.profile)
        context['filter_job_offer'] = FilterJobOfferForm(self.request.GET)
        return context


@login_required
def create_resume(request):
    user = request.user
    try:
        resume = Resume.objects.get(user_profile=user.profile).resume_file
    except Resume.DoesNotExist:
        resume = None
    if resume is None:
        generated_resume = ResumePdfRender.render(user)
        if generated_resume is not None:
            Resume.objects.create(resume_file=File(generated_resume, name='user%s_resume.pdf' % user.profile.pk),
                                  user_profile=user.profile)
            resume = generated_resume.getvalue()
        else:
            return HttpResponse("Error Rendering PDF", status=500)
    response = HttpResponse(resume, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="resume.pdf"'
    return response
