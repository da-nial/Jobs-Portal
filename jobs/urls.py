from django.urls import path

from jobs import views

app_name = 'jobs'
urlpatterns = [
    # ex: /job_offers/5
    path('job_offers/<int:pk>/', views.JobOffersView.as_view(), name='job_offers'),
    path('profile/<int:pk>/', views.UserProfileView.as_view(), name='user_profile'),
    path('company/<int:pk>/', views.CompanyView.as_view(), name='company'),
    # ex: /edit_profile
    path('edit_profile', views.edit_profile_view, name='edit_profile'),
    # ex: /edit_profile/delete_skill/5
    path('edit_profile/delete_skill/<skill_id>/', views.delete_skill, name='delete_skill'),
    # ex: /edit_profile/delete_educational_background/5
    path('edit_profile/delete_educational_background/<educational_background_id>/',
         views.delete_educational_background, name='delete_educational_background'),
]
