from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import CustomUserManager
from django.db import IntegrityError
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(verbose_name=_('email address'),
                              unique=True,
                              error_messages={
                                  'unique': "A user with that email already exists.",
                              },
                              )

    verification_token = models.CharField(max_length=50, null=True, unique=True, db_index=True)
    is_email_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def refresh_verification_token(self):
        while True:
            new_verification_token = get_random_string(50)
            try:
                self.verification_token = new_verification_token
                self.save()
                break
            except IntegrityError:
                continue

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
