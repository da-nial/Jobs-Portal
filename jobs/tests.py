import datetime

from django.contrib.auth import authenticate
from django.test import TestCase

from django.urls import reverse

from authentication.models import CustomUser
from .models import Company, JobOffer, UserProfile, Skill, EducationalLevel, EducationalBackground
from django.contrib.messages import get_messages


class CompanyModelTests(TestCase):
    def test_successful_company_with_logo_creation(self):
        company = Company(name='test_1', logo='images/test.jpg',
                          telephone_number='test_phone', link='test.com')
        self.assertTrue(company.logo.url, 'media/images/test.jpg')

    def test_successful_company_without_logo_creation(self):
        company = Company(name='test_2', telephone_number='test_phone', link='test.com')
        company.save()


def create_skills(*skill_title_list):
    skills = []
    for skill_title in skill_title_list:
        skills.append(Skill.objects.create(title=skill_title))

    return skills


def create_company():
    return Company(name='test_company',
                   link='test.com',
                   telephone_number=98,
                   address='48rd Fl., No.289, Shahid Kolahdouz St., Shariati St., tehran, Iran',
                   logo='images/test.jpg')


def create_job_offer(skill_list=None,
                     company=None,
                     minimum_degree=EducationalLevel.BACHELORS_DEGREE,
                     is_enabled=True,
                     city='Tehran'):
    if company is None:
        company = create_company()

    job_offer = JobOffer(title='test_title',
                         description='test_description',
                         company=company,
                         minimum_degree=minimum_degree,
                         is_enabled=is_enabled,
                         city=city)
    company.save()
    job_offer.save()
    if skill_list:
        job_offer.skills_required.set(skill_list)
    return job_offer


def create_user(email='negar@gmail.com',
                password='ComplicatedPassword1'):
    return CustomUser.objects.create_user(email=email,
                                          password=password,
                                          first_name='Negar',
                                          last_name='Raei')


def create_profile(user, skill_list=None, city_of_residence='Tehran', educational_background_level_list=None):
    if educational_background_level_list is None:
        educational_background_level_list = [EducationalLevel.ASSOCIATE, EducationalLevel.DIPLOMA]
    if skill_list is None:
        skill_list = create_skills('test_skill_2')
    profile = UserProfile.objects.create(
        user=user,
        mobile_number='09012223344',
        phone_number='02122334455',
        address='48rd Fl., No.289, Shahid Kolahdouz St., Shariati St., Tehran, Iran',
        gender='F',
        marital_status='S',
        city_of_residence=city_of_residence,
        bio='20 year old ui designer from Iran',
    )
    for edu_back_lvl in educational_background_level_list:
        EducationalBackground.objects.create(field='Computer Engineering',
                                             institute='Sharif University',
                                             level=edu_back_lvl,
                                             start_year=1397,
                                             finish_year=1400,
                                             is_currently_studying=True,
                                             user_profile=profile)
    profile.skills.set(skill_list)
    return profile


class JobOfferPageTests(TestCase):
    def setUp(self) -> None:
        password = 'ComplicatedPassword1'
        user = create_user(password=password)
        create_profile(user)
        email = user.email
        self.client.login(email=email, password=password)

    def test_not_found_skill(self):

        response = self.client.get(reverse('jobs:job_offers', args=[1]))
        self.assertEqual(response.status_code, 404)

    def test_found_skill_link(self):
        job_offer = create_job_offer()
        response = self.client.get(reverse('jobs:job_offers', args=[1]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['joboffer'], job_offer)

    def test_disabled_job(self):
        create_job_offer(is_enabled=False)
        response = self.client.get('/en' + reverse('jobs:job_offers', args=[1]))
        self.assertContains(response, 'this job is disabled')

    def tearDown(self) -> None:
        self.client.logout()


class UserProfileModelTest(TestCase):
    """
    UserProfileModel tests. As there were no custom methods, only successful
     creation of profile instance is tested.
    """

    def setUp(self) -> None:
        self.user_1 = create_user()
        create_profile(self.user_1)

    def test_user_profile_is_created_successfully(self):
        profile = self.user_1.profile

        self.assertIsNotNone(profile)
        self.assertEqual(str(profile), 'Negar Raei')


class DisableJobsTest(TestCase):

    def test_job_offer_managers(self):
        company = create_company()
        # enabled job
        create_job_offer(company=company, is_enabled=True)
        # disabled job
        create_job_offer(company=company, is_enabled=False)
        self.assertEqual(JobOffer.objects.all().count(), 2)
        self.assertEqual(JobOffer.enabled.all().count(), 1)


class MainPageOfferSuggestionTest(TestCase):

    def setUp(self) -> None:
        all_skills = create_skills('django', 'docker', '.NET', 'cpp')
        profile_skills = all_skills[1:]
        self.password = 'ComplicatedPassword1'
        related_city = 'Isfahan'
        self.user = create_user(email='user@email.com', password=self.password)
        create_profile(user=self.user,
                       city_of_residence=related_city,
                       skill_list=profile_skills,
                       educational_background_level_list=[EducationalLevel.BACHELORS_DEGREE, EducationalLevel.DIPLOMA])
        self.client.login(email=self.user.email, password=self.password)
        self.related_city = related_city
        self.unrelated_city = 'Tehran'
        self.related_edu_level = EducationalLevel.ASSOCIATE
        self.unrelated_edu_level = EducationalLevel.MASTERS_DEGREE
        self.related_skills = profile_skills[1:]
        self.unrelated_skills = all_skills

    def test_get_le_educational_levels(self):
        self.assertEqual(set(EducationalLevel.BACHELORS_DEGREE.get_le_educational_levels()),
                         {EducationalLevel.OTHERS,
                          EducationalLevel.DIPLOMA,
                          EducationalLevel.ASSOCIATE,
                          EducationalLevel.BACHELORS_DEGREE})

    def test_get_maximum_educational_level(self):
        self.assertEqual(self.user.profile.get_maximum_educational_level(), EducationalLevel.BACHELORS_DEGREE)

    def test_city_is_checked(self):
        offer_with_unrelated_address = create_job_offer(
            city=self.unrelated_city,
            skill_list=self.related_skills,
            minimum_degree=self.related_edu_level)
        response = self.client.get(reverse('jobs:main'))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(offer_with_unrelated_address, response.context['appropriate_offers'])

    def test_skills_are_checked(self):
        offer_with_unrelated_skills = create_job_offer(
            city=self.related_city,
            skill_list=self.unrelated_skills,
            minimum_degree=self.related_edu_level)
        response = self.client.get(reverse('jobs:main'))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(offer_with_unrelated_skills, response.context['appropriate_offers'])

    def test_minimum_degree_is_checked(self):
        offer_with_unrelated_edu_level = create_job_offer(
            city=self.related_city,
            skill_list=self.related_skills,
            minimum_degree=self.unrelated_edu_level)
        response = self.client.get(reverse('jobs:main'))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(offer_with_unrelated_edu_level, response.context['appropriate_offers'])

    def test_related_offer(self):
        related_offer = create_job_offer(
            city=self.related_city,
            skill_list=self.related_skills,
            minimum_degree=self.related_edu_level)
        response = self.client.get(reverse('jobs:main'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(1, len(response.context['appropriate_offers']))
        self.assertIn(related_offer, response.context['appropriate_offers'])

    def tearDown(self) -> None:
        self.client.logout()


class WarningRequirementOffer(TestCase):
    def setUp(self) -> None:
        self.company = Company.objects.create(name='divar', link='divar.ir', telephone_number='02188888888')
        self.skill_1 = Skill.objects.create(title='skill1')
        self.skill_2 = Skill.objects.create(title='skill2')
        self.skill_3 = Skill.objects.create(title='skill3')
        self.user_1 = CustomUser.objects.create_user(email='negar@gmail.com',
                                                     password='ComplicatedPassword1',
                                                     first_name='Negar',
                                                     last_name='Raei')
        self.job_offer = JobOffer.objects.create(title='backend', minimum_work_experience=0, minimum_degree='M',
                                                 type_of_cooperation='full_time', city='نهران',
                                                 company=self.company)
        self.job_offer.skills_required.add(self.skill_1)

    def test_requirement_true(self):
        user_1_profile = UserProfile.objects.create(
            user=self.user_1,
            city_of_residence='نهران',
        )
        user_1_profile.skills.add(self.skill_1, self.skill_2)
        self.education_background = EducationalBackground.objects.create(field='doctor', level='DO', start_year=1390,
                                                                         institute='aaa',
                                                                         is_currently_studying=False,
                                                                         finish_year=1395,
                                                                         user_profile=user_1_profile)
        self.assertEqual(True, self.user_1.has_requirement_for_offer(self.job_offer))

    def test_city_requirement_false(self):
        user_1_profile = UserProfile.objects.create(
            user=self.user_1,
            city_of_residence='کرج',
        )
        user_1_profile.skills.add(self.skill_1, self.skill_2)
        self.education_background = EducationalBackground.objects.create(field='doctor', level='DO', start_year=1390,
                                                                         institute='aaa',
                                                                         is_currently_studying=False,
                                                                         finish_year=1395,
                                                                         user_profile=user_1_profile)
        self.assertEqual(False, self.user_1.has_requirement_for_offer(self.job_offer))

    def test_skill_requirement_false(self):
        user_1_profile = UserProfile.objects.create(
            user=self.user_1,
            city_of_residence='نهران',
        )
        user_1_profile.skills.add(self.skill_3)
        self.education_background = EducationalBackground.objects.create(field='doctor', level='DO', start_year=1390,
                                                                         institute='aaa',
                                                                         is_currently_studying=False,
                                                                         finish_year=1395,
                                                                         user_profile=user_1_profile)
        self.assertEqual(False, self.user_1.has_requirement_for_offer(self.job_offer))

    def test_education_requirement_false(self):
        user_1_profile = UserProfile.objects.create(
            user=self.user_1,
            city_of_residence='نهران',
        )
        user_1_profile.skills.add(self.skill_1, self.skill_2)
        self.education_background = EducationalBackground.objects.create(field='doctor', level='DI', start_year=1390,
                                                                         institute='aaa',
                                                                         is_currently_studying=False,
                                                                         finish_year=1395,
                                                                         user_profile=user_1_profile)
        self.assertEqual(False, self.user_1.has_requirement_for_offer(self.job_offer))
