from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _


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