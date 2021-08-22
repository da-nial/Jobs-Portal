from django import forms

from jobs.models import UserProfile, Skill, EducationalBackground, JobOffer
from proxy.models.city_api import CitiesProxy
from django.utils.translation import ugettext_lazy as _


class EditProfilePageFormMixin:

    def save_profile_form(self, profile):
        raise NotImplementedError


class EditProfileForm(forms.ModelForm, EditProfilePageFormMixin):
    city_of_residence = forms.ChoiceField(choices=())
    first_name = forms.CharField(label=_('first name'), required=False)
    last_name = forms.CharField(label=_('last name'), required=False)

    def __init__(self, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.fields['city_of_residence'].choices = CitiesProxy.get_instance().get_city_name_tuple()
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
    skills = forms.ModelMultipleChoiceField(queryset=Skill.objects.all(), required=False, label=_('Skills'))

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


class JobOfferForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(JobOfferForm, self).__init__(*args, **kwargs)
        self.fields['city'].choices = CitiesProxy.get_instance().get_city_name_tuple()

    city = forms.ChoiceField(choices=())

    class Meta:
        model = JobOffer
        exclude = []


class UserProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.fields['city_of_residence'].choices = CitiesProxy.get_instance().get_city_name_tuple()

    city_of_residence = forms.ChoiceField(choices=())

    class Meta:
        model = UserProfile
        exclude = []
