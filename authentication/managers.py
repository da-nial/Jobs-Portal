from django.contrib.auth.base_user import BaseUserManager


class CustomUserManager(BaseUserManager):
    """
    CustomUser model manager, where email is the unique identifier
     for authentication instead of username.
    """

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email and password.
        extra_fields are the remaining fields of CustomUser model
         such as is_active and is_superuser.
        """
        if not email:
            raise ValueError("Email has not been set. Users must have email.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_user(self, email, password, **extra_fields):
        """
        Create and save a regular user (as opposed to superuser), with email as identifier.
        Note that is_superuser can't be set to true,
         otherwise ValueError will be raised.
        """
        extra_fields.setdefault('is_superuser', False)

        if extra_fields.get('is_superuser') is True:
            raise ValueError("Regular Users can't have is_superuser=True")

        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a superuser, with email as identifier.
        Note that is_staff and is_superuser must be true,
         otherwise ValueError will be raised.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self._create_user(email, password, **extra_fields)
