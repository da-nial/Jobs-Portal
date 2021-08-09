from django.db import models


# Create your models here.

class Company(models.Model):
    name = models.CharField(max_length=255, unique=True)
    address = models.TextField(blank=True)
    logo = models.ImageField(upload_to='images', blank=True)
    description = models.TextField(blank=True)
    link = models.URLField(max_length=200)
    telephone_number = models.CharField(max_length=12)


class TagsOfSkill(models.Model):
    skill = models.CharField(max_length=20)


class JobOffer(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=500, blank=True)
    salary = models.IntegerField(blank=True, null=True)
    minimum_work_experience = models.IntegerField(default=0)
    CHOICES_TIME = [
        ('full_time', 'full time'),
        ('part_time', 'part time'),
    ]
    type_of_cooperation = models.CharField(choices=CHOICES_TIME, max_length=10,default='full time')
    CHOICES_DEGREE = [
        ('Diploma', 'دیپلم'),
        ('Bachelor', 'کارشناسی'),
        ('Master', 'کارشناسی ارشد'),
        ('PHD', 'دکترا'),
    ]
    minimum_degree = models.CharField(choices=CHOICES_DEGREE, max_length=1000, default='Diploma')
    skills_required = models.ManyToManyField(TagsOfSkill)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)



