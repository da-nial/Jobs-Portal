from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'auth'
urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.login_user, name='login'),
    path('send-email-verification/', views.send_email_verification, name='send-email-verification'),
    path('verify/<str:token>/', views.verify_email, name='verify'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('password-reset/', views.CustomPasswordResetView.as_view(),
         name='password_reset'),
    path('password-reset-confirm/<uidb64>/<token>/',
         views.CustomPasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('password-reset-done/',
         views.CustomPasswordResetDoneView.as_view(),
         name='password_reset_done'),
    path('password-reset-complete/',
         views.CustomPasswordResetCompleteView.as_view(),
         name='password_reset_complete'),
]
