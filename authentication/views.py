from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import CreateView

from authentication.forms import UserForm
from authentication.models import CustomUser


class RegisterView(CreateView):
    model = CustomUser
    template_name = 'register.html'
    form_class = UserForm
    success_url = settings.LOGIN_URL


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
            context['error'] = 'Email and password must be provided.'
            return HttpResponse(render(request, 'login.html', context), status=200)

        if user is not None:
            login(request, user)
            return HttpResponse(f"Hey {str(user)}! You're now logged in.", status=200)
        else:
            context['error'] = 'Wrong credentials.'
            return HttpResponse(render(request, 'login.html', context), status=200)
