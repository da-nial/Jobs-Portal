from django.urls import path

from jobs import views

app_name = 'jobs'
urlpatterns = [
    # ex: /job_offers/5
    path('job_offers/<int:pk>/', views.JobOffersView.as_view(), name='job_offers'),
    path('profile/<int:pk>/', views.UserProfileView.as_view(), name='user_profile')
]
