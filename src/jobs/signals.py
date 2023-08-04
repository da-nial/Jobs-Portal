from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from jobs.mail_service import send_application_state
from jobs.models import Application, Company, JobOffer
from website import settings


@receiver(pre_save, sender=Application, )
def pre_save_signal_application(sender, instance, **kwargs):
    if instance.id is None:
        return
    previous = Application.objects.get(id=instance.id)
    if previous.state != instance.state:
        send_application_state(previous.user, instance.state)


@receiver(post_save, sender=Company)
def post_save_signal_cache_handle_for_company(sender, instance, **kwargs):
    for language_code in settings.LANGUAGES:
        key = make_template_fragment_key('Company', (instance.id, language_code[0]))
        cache.delete(key)


@receiver(post_save, sender=JobOffer)
def post_save_signal_cache_handle_for_job_offer(sender, instance, **kwargs):
    for language_code in settings.LANGUAGES:
        key = make_template_fragment_key('JobOffer', (instance.id, language_code[0]))
        cache.delete(key)


@receiver(pre_save, sender=JobOffer)
def pre_save_signal_for_send_tagged_job_email(instance, **kwargs):
    if instance.id is None:
        return
    previous = JobOffer.objects.get(id=instance.id)
    if previous.is_enabled is False and instance.is_enabled:
        JobOffer.send_inform_email_to_tagged_users(instance)
