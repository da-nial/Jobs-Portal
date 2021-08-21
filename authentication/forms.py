from django import forms
from django.core.validators import MinLengthValidator, RegexValidator
from django.utils.translation import ugettext_lazy as _
from jobs.models import UserProfile
from .models import CustomUser


class UserForm(forms.ModelForm):
    password = forms.CharField(
        label=_('Password'),
        max_length=100,
        widget=forms.PasswordInput(),
        validators=[
            MinLengthValidator(limit_value=8, message=_('password should be at least 8 character')),
            RegexValidator(regex=r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]*$",
                           message=_('password should contain at least one letter and one number'))
        ],
    )

    class Meta:
        fields = ['first_name', 'last_name', 'email']
        model = CustomUser

    def save(self, commit=True):
        user = super(UserForm, self).save(commit=False)
        user.set_password(self.cleaned_data.get('password'))
        if commit:
            user.save()
            UserProfile(user=user).save()
        return user
