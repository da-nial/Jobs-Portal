from django.db import models
from django.db.models import Q, Count, F


class EnabledManager(models.Manager):
    def get_queryset(self):
        return super(EnabledManager, self).get_queryset().filter(is_enabled=True)

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
