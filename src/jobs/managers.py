from django.core.exceptions import FieldError
from django.db import models
from django.db.models import Q, Count, F


class EnabledManager(models.Manager):
    def get_queryset(self):
        return JobQuerySet(self.model, using=self._db).filter(is_enabled=True)

    def appropriate_offers_for_profile(self, profile):
        return self.get_queryset().filter(
            city=profile.city_of_residence,
            minimum_degree__in=profile.get_maximum_educational_level().get_le_educational_levels()
        ).alias(
            req_skill_count=Count('skills_required', distinct=True),
            skills_count=Count(
                'skills_required',
                filter=Q(skills_required__userprofile=profile),
                distinct=True
            )
        ).filter(
            req_skill_count=F('skills_count')
        ).order_by('-salary')[:10]


class JobQuerySet(models.QuerySet):
    def filter_job(self, title_search, minimum_work_experience, category, city, company=None):
        queryset = self.filter(
            minimum_work_experience__gte=minimum_work_experience
        )

        if category != "AL":
            queryset = queryset.filter(category=category)

        if city != "AL":
            queryset = queryset.filter(city=city)

        if title_search:
            try:
                queryset = queryset.filter(title__search=title_search)
            except FieldError:
                queryset = queryset.filter(title__icontains=title_search)

        if company:
            queryset.filter(company=company)
        return queryset
