from django.contrib import admin
from .models import JobOffer,TagsOfSkill
# Register your models here.
from jobs.models import Company


admin.site.register(Company)
admin.site.register(JobOffer)
admin.site.register(TagsOfSkill)

