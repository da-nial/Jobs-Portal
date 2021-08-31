from django import template
from django.template.defaultfilters import stringfilter
from django.utils.translation import get_language

NUMBER_MAP = {
    "0": "۰",
    "1": "۱",
    "2": "۲",
    "3": "۳",
    "4": "۴",
    "5": "۵",
    "6": "۶",
    "7": "۷",
    "8": "۸",
    "9": "۹"
}

register = template.Library()


@register.filter()
@stringfilter
def translate_numbers(input_string):
    if get_language() == 'fa':
        try:
            return "".join([NUMBER_MAP[digit] for digit in input_string])
        except KeyError:
            return input_string
    return input_string
