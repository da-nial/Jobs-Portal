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
    job_offer = JobOffer(title='test_title', description='test_description', company=company)
    company.save()
    skill.save()
    job_offer.save()
    job_offer.skills_required.set([skill])
    return job_offer


class JobOfferPageTests(TestCase):
    def test_not_found_skill(self):
        response = self.client.get(reverse('jobs:job_offers', args=[1]))
        self.assertEqual(response.status_code, 404)

    def test_found_skill_link(self):
        job_offer = create_job_offer()
        response = self.client.get(reverse('jobs:job_offers', args=[1]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['joboffer'], job_offer)


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
