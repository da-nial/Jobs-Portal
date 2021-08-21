from django.contrib import admin
from .models import *


class UserProfileAdmin(admin.ModelAdmin):
    model = UserProfile
    filter_horizontal = ('skills',)


admin.site.register(Company)
admin.site.register(JobOffer)
admin.site.register(Skill)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(EducationalBackground)
admin.site.register(Application)
