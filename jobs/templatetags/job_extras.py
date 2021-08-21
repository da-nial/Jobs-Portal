from django import template
from authentication.models import CustomUser
register = template.Library()


@register.filter
def has_pending_application_for_offer(user: CustomUser, offer):
    return user.has_pending_application_for_offer(offer)


@register.filter
def get_applications_for_offer(user: CustomUser, offer):
    return user.get_applications_for_offer(offer)

