from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView
from authentication.models import CustomUser
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView, PasswordResetDoneView, \
    PasswordResetCompleteView
from .forms import UserForm


class RegisterView(SuccessMessageMixin, CreateView):
    model = CustomUser
    template_name = 'register.html'
    form_class = UserForm
    success_url = settings.LOGIN_URL
    success_message = _("Your account has been created successfully.")


def login_user(request):
    if request.method == 'GET':
        return HttpResponse(render(request, 'login.html'))
    if request.method == 'POST':
        context = {}

        if request.POST.get('email') and request.POST.get('password'):
            user = authenticate(
                request,
                email=request.POST['email'],
                password=request.POST['password']
            )
        else:
            context['error'] = _('Email and password must be provided.')
            return render(request, 'login.html', context, status=200)

        if user is not None:
            login(request, user)
            if 'next' in request.POST:
                return HttpResponseRedirect(request.POST.get('next'))
            return HttpResponseRedirect(reverse('jobs:main'))
        else:
            context['error'] = _('Wrong credentials.')
            return render(request, 'login.html', context, status=200)


@login_required
def send_email_verification(request):
    if request.method != "POST":
        return HttpResponse("Bad request (This url only accepts post requests)", status=400)

    if request.user.is_email_verified:
        return HttpResponse('Your email is already verified!')

    user = request.user
    user.refresh_verification_token()

    domain = get_current_site(request).domain
    mail_subject = 'Activate your Adams account.'
    token = user.verification_token
    message = render_to_string('email_templates/verification-email.html', {
        'user': request.user,
        'domain': domain,
        'token': token,
    })
    to_email = request.user.email
    email = EmailMessage(
        mail_subject, message, to=[to_email]
    )
    email.send()
    messages.success(request, f"Verification email sent to {request.user.email}")

    return HttpResponseRedirect(reverse("jobs:user_profile"))


def verify_email(request, token):
    try:
        user = CustomUser.objects.get(verification_token=token)

        user.verification_token = None
        user.is_email_verified = True
        user.save()
        messages.success(request, 'Thank you for your email confirmation.')
        return HttpResponseRedirect('/')

    except CustomUser.DoesNotExist:
        return HttpResponse('Verification link is invalid!')


class CustomPasswordResetView(PasswordResetView):
    email_template_name = 'email_templates/password_reset_email.html'
    template_name = 'password_reset.html'
    success_url = reverse_lazy('auth:password_reset_done')


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'password_reset_confirm.html'
    success_url = reverse_lazy('auth:password_reset_complete')


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'password_reset_done.html'


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'password_reset_complete.html'
