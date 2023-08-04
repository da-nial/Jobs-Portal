from jobs.models import UserProfile
from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm


class UserForm(UserCreationForm):
    class Meta:
        fields = ['first_name', 'last_name', 'email']
        model = CustomUser

    def save(self, commit=True):
        user = super(UserForm, self).save(commit=False)
        if commit:
            user.save()
            UserProfile(user=user).save()
        return user
