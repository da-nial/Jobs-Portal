from django.urls import path

from . import views

app_name = 'auth'
urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.login_user, name='login'),
    path('send-email-verification/', views.send_email_verification, name='send-email-verification'),
    path('verify/<str:token>/', views.verify_email, name='verify'),
]
