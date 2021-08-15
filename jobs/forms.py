from django import forms

from jobs.models import UserProfile, Skill, EducationalBackground


class EditProfilePageFormMixin:

    def save_profile_form(self, profile):
        raise NotImplementedError


class EditProfileForm(forms.ModelForm, EditProfilePageFormMixin):
    first_name = forms.CharField(label='first name', required=False)
    last_name = forms.CharField(label='last name', required=False)

    def __init__(self, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        if self.instance:
            self.initial['first_name'] = self.instance.user.first_name
            self.initial['last_name'] = self.instance.user.last_name

    class Meta:
        model = UserProfile
        fields = ['mobile_number', 'phone_number', 'address', 'military_service_status', 'gender',
                  'marital_status', 'city_of_residence', 'bio']

    def save_profile_form(self, profile):
        profile = super(EditProfileForm, self).save()
        user = profile.user
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.save()
        return user


class SkillForm(forms.Form):
    skills = forms.ModelMultipleChoiceField(queryset=Skill.objects.all(), required=False)

    def save_profile_form(self, profile):
        for skill in self.cleaned_data.get('skills'):
            profile.skills.add(skill)
        profile.save()


class EducationalBackgroundForm(forms.ModelForm):
    class Meta:
        model = EducationalBackground
        fields = ['field', 'institute', 'level', 'start_year', 'finish_year', 'is_currently_studying']

    def save_profile_form(self, profile):
        educational_background = super(EducationalBackgroundForm, self).save(commit=False)
        educational_background.user_profile = profile
        educational_background.save()
        return educational_background
