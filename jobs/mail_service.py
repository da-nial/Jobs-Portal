from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from jobs.models import AltEmail
from django.http import HttpRequest


def send_application_state(user, state):
    state_templates = {
        'A': 'email_templates/accepted_job_application.html',
        'R': 'email_templates/reject_job_application.html',
        'P': 'email_templates/pending_job_application.html',
    }
    message = render_to_string(state_templates[state], {
        'user': user,
    })
    to_email = user.email
    mail_subject = _('your job application state changed')
    email = EmailMessage(
        mail_subject, message, to=[to_email]
    )
    email.send()


def send_verification_email(request, alt_email: AltEmail):
    domain = get_current_site(request).domain
    mail_subject = 'Alternative Email Verification'
    token = alt_email.verification_token
    message = render_to_string('email_templates/alternative_email_verification.html', {
        'user': request.user,
        'domain': domain,
        'token': token,
    })
    to_email = alt_email.address
    email_message = EmailMessage(
        mail_subject, message, to=[to_email]
    )
    email_message.send()


def send_offer_suggestion(user, offer):
    request = HttpRequest()
    request.META['HTTP_HOST'] = settings.SITE_URL
    message = render_to_string('email_templates/offer_suggestion.html', {
        'user': user,
        'offer': offer,
        'request': request,
    })
    to_email = user.email
    mail_subject = _('Job Recommendation')
    email = EmailMessage(
        mail_subject, message, to=[to_email]
    )
    email.content_subtype = "html"
    email.send()


def send_offer_inform(user, offer):
    message = render_to_string('email_templates/offer_inform.html', {
        'user': user,
        'offer': offer,
        'domain': settings.SITE_URL,
    })
    to_email = user.email
    mail_subject = _('inform tagged job')
    email = EmailMessage(
        mail_subject, message, to=[to_email]
    )
    email.send()
