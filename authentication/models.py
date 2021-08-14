from django.db import models

from django.contrib.auth.models import AbstractUser

from .managers import CustomUserManager


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(verbose_name='email address',
                              unique=True,
                              error_messages={
                                  'unique': "A user with that email already exists.",
                              },
                              )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        if self.first_name or self.last_name:
            return self.get_full_name()
        else:
            return self.email

    def has_pending_application_for_offer(self, offer):
        from jobs.models import Application
        return offer.applications.filter(user=self, state=Application.State.PENDING).exists()

    def get_applications_for_offer(self, offer):
        return offer.applications.filter(user=self)
