from django.conf import settings
from django.shortcuts import render
from django.views.generic import CreateView

from authentication.forms import UserForm
from authentication.models import CustomUser


class RegisterView(CreateView):
    model = CustomUser
    template_name = 'register.html'
    form_class = UserForm
    success_url = settings.LOGIN_URL
