from django.urls import path

from . import views

app_name = 'auth'
urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.login_user, name='login'),
]
