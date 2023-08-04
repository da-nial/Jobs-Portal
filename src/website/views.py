from django.http import HttpResponseNotFound
from django.conf import settings
from django.template.loader import render_to_string


def error_404(request, exception):
    data = {'email_address': settings.EMAIL_HOST_USER}
    return HttpResponseNotFound(render_to_string('404.html', context=data, request=request))
