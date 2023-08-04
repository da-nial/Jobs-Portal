from celery import shared_task
from jobs.mail_service import send_offer_suggestion, send_offer_inform
from jobs.models import JobOffer


@shared_task(ignore_result=True)
def send_offer_suggestion_email(user_id, offer_id):
    if not JobOffer.objects.filter(pk=offer_id).exists():
        return
    offer = JobOffer.objects.get(pk=offer_id)
    if not offer.is_enabled:
        return

    from authentication.models import CustomUser
    if not CustomUser.objects.filter(pk=user_id).exists():
        return
    user = CustomUser.objects.get(pk=user_id)

    if user.is_email_verified:
        send_offer_suggestion(user, offer)


@shared_task(ignore_result=True)
def send_tagged_offer_email(user_id, offer_id):
    from authentication.models import CustomUser
    user = CustomUser.objects.get(pk=user_id)

    offer = JobOffer.objects.get(pk=offer_id)

    if user.is_email_verified:
        send_offer_inform(user, offer)
