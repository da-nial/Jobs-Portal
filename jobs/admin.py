from django.contrib import admin
# Register your models here.
from .models import Company, JobOffer, TagsOfSkill


admin.site.register(Company)
admin.site.register(JobOffer)
admin.site.register(TagsOfSkill)
