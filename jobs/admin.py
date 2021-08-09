from django.contrib import admin

from .models import Company, JobOffer, Skill, UserProfile, EducationalBackground

admin.site.register(Company)
admin.site.register(JobOffer)
admin.site.register(Skill)
admin.site.register(UserProfile)
admin.site.register(EducationalBackground)
