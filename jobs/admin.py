from django.contrib import admin

from .forms import JobOfferForm, UserProfileForm
from .models import *


@admin.register(JobOffer)
class JobOfferAdmin(admin.ModelAdmin):
    form = JobOfferForm


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    model = UserProfile
    filter_horizontal = ('skills',)
    form = UserProfileForm


admin.site.register(Company)
admin.site.register(Skill)
admin.site.register(AltEmail)
admin.site.register(EducationalBackground)
admin.site.register(Application)
