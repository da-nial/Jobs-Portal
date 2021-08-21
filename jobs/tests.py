import datetime

from django.contrib.auth import authenticate
from django.test import TestCase

from django.urls import reverse

from authentication.models import CustomUser
from .models import Company, JobOffer, UserProfile, Skill


class CompanyModelTests(TestCase):
    def test_successful_company_with_logo_creation(self):
        company = Company(name='test_1', logo='images/test.jpg',
                          telephone_number='test_phone', link='test.com')
        self.assertTrue(company.logo.url, 'media/images/test.jpg')

    def test_successful_company_without_logo_creation(self):
        company = Company(name='test_2', telephone_number='test_phone', link='test.com')
        company.save()


def create_job_offer():
    company = Company(name='test_company', link='test.com', telephone_number=98)
    skill = Skill(title='test_skill')
    job_offer = JobOffer(title='test_title', description='test_description', company=company, is_enabled=False)
    company.save()
    skill.save()
    job_offer.save()
    job_offer.skills_required.set([skill])
    return job_offer


class JobOfferPageTests(TestCase):
    def setUp(self) -> None:
        user = CustomUser.objects.create(email='amin@gmail.com', is_active=True)
        user.set_password('amin')
        user.save()

        profile = UserProfile(user=user)
        profile.save()

    def test_not_found_skill(self):
        self.client.login(username='amin@gmail.com', password='amin')
        response = self.client.get(reverse('jobs:job_offers', args=[1]))
        self.assertEqual(response.status_code, 404)

    def test_found_skill_link(self):
        job_offer = create_job_offer()
        self.client.login(username='amin@gmail.com', password='amin')
        response = self.client.get(reverse('jobs:job_offers', args=[1]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['joboffer'], job_offer)

    def test_disabled_job(self):
        job_offer = create_job_offer()
        self.client.login(username='amin@gmail.com', password='amin')
        response = self.client.get(reverse('jobs:job_offers', args=[1]))
        self.assertContains(response, 'this job is disabled')


class UserProfileModelTest(TestCase):
    """
    UserProfileModel tests. As there were no custom methods, only successful
     creation of profile instance is tested.
    """

    def setUp(self) -> None:
        self.user_1 = CustomUser.objects.create_user(email='negar@gmail.com',
                                                     password='ComplicatedPassword1',
                                                     first_name='Negar',
                                                     last_name='Raei')
        user_1_profile = UserProfile.objects.create(
            user=self.user_1,
            mobile_number='09012223344',
            phone_number='02122334455',
            address='48rd Fl., No.289, Shahid Kolahdouz St., Shariati St., Tehran, Iran',
            gender='F',
            marital_status='S',
            city_of_residence='Tehran',
            bio='20 year old ui designer from Iran',
        )

    def test_user_profile_is_created_successfully(self):
        profile = self.user_1.profile

        self.assertIsNotNone(profile)
        self.assertEqual(str(profile), 'Negar Raei Profile')


class DisableJobsTest(TestCase):

    def test_job_offer_managers(self):
        company = Company.objects.create(name='test_company',
                                         link='test.ir',
                                         telephone_number='test_phone')
        # enabled job
        JobOffer.objects.create(title='enabled_job',
                                type_of_cooperation='full_time',
                                company=company,
                                is_enabled=True
                                )
        # disabled job
        JobOffer.objects.create(title='disabled_job',
                                type_of_cooperation='full_time',
                                company=company,
                                is_enabled=False
                                )
        self.assertEqual(JobOffer.objects.all().count(), 2)
        self.assertEqual(JobOffer.enabled.all().count(), 1)
