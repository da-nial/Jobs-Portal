from django.db.models.signals import pre_save
from django.dispatch import receiver

from jobs.mail_service import send_application_state
from jobs.models import Application


@receiver(pre_save, sender=Application,)
def pre_save_signal_application(sender, instance, **kwargs):
    if instance.id is None:
        return
    previous = Application.objects.get(id=instance.id)
    if previous.state != instance.state:
        send_application_state(previous.user, instance.state)

