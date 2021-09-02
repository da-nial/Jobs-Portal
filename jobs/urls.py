from django.urls import path

from jobs import views

app_name = 'jobs'
urlpatterns = [
    # ex: /job_offers/5
    path('job_offers/<int:pk>/', views.JobOffersView.as_view(), name='job_offers'),
    path('', views.MainView.as_view(), name='main'),
    path('profile/', views.UserProfileView.as_view(), name='user_profile'),
    path('company/<int:pk>/', views.CompanyView.as_view(), name='company'),
    # ex: /edit_profile
    path('edit_profile/', views.edit_profile_view, name='edit_profile'),
    # ex: /edit_profile/delete_skill/5
    path('edit_profile/delete_skill/<skill_id>/', views.delete_skill, name='delete_skill'),
    # ex: /edit_profile/delete_educational_background/5
    path('edit_profile/delete_educational_background/<educational_background_id>/',
         views.delete_educational_background, name='delete_educational_background'),
    path('edit_profile/alt_email/add/', views.add_alt_email, name='add_alt_email'),
    path('edit_profile/alt_email/delete/<int:alt_email_pk>/',
         views.delete_alt_email,
         name='delete_alt_email'),
    path('send-email-verification/<int:email_pk>/',
         views.send_email_verification,
         name='send-email-verification'),
    path('verify/<str:token>/', views.verify, name='verify'),
    # ex: /job_offers/5/apply
    path('job_offers/<int:pk>/apply/', views.apply, name='apply'),
    path('create_resume/', views.create_resume, name='create_resume'),

]
