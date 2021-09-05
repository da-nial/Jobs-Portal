from unittest.mock import patch, MagicMock
from django.utils.crypto import get_random_string
from django.test import TestCase
from django.urls import reverse
from django.utils.translation import gettext
from authentication.models import CustomUser
from jobs.models import UserProfile, Skill, JobOffer, EducationalLevel, EducationalBackground, Company


class LoginViewTest(TestCase):
    def setUp(self) -> None:
        super().setUp()

        user = CustomUser.objects.create(email='sara@gmail.com', is_active=True)
        user.set_password('salamsalam1')
        user.save()

    def test_successful_login(self):
        data = {'email': 'sara@gmail.com', 'password': 'salamsalam1'}
        response = self.client.post(reverse('auth:login'), data=data)
        self.assertRedirects(response, reverse('jobs:main'), fetch_redirect_response=False)

    def test_successful_redirect_to_login(self):
        self.client.logout()
        response = self.client.get(reverse('jobs:edit_profile'))
        self.assertRedirects(response, reverse('auth:login') + '?next=' + reverse('jobs:edit_profile'))

    def test_successful_redirect_from_login(self):
        self.client.logout()
        data = {'email': 'sara@gmail.com', 'password': 'salamsalam1', 'next': reverse('jobs:edit_profile')}
        response = self.client.post(reverse('auth:login'), data=data)
        self.assertRedirects(response, reverse('jobs:edit_profile'), fetch_redirect_response=False)

    def test_wrong_password(self):
        data = {'email': 'sara@gmail.com', 'password': 'sadsad'}
        response = self.client.post(reverse('auth:login'), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertEqual(response.context['error'], gettext('Wrong credentials.'))

    def test_wrong_email(self):
        data = {'email': 'sara1@gmail.com', 'password': 'salamsalam1'}
        response = self.client.post(reverse('auth:login'), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertEqual(response.context['error'], gettext('Wrong credentials.'))

    def test_password_is_empty(self):
        data = {'email': 'sara@gmail.com'}
        response = self.client.post(reverse('auth:login'), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertEqual(response.context['error'], gettext('Email and password must be provided.'))

    def test_email_is_empty(self):
        data = {'password': 'salamsalam1'}
        response = self.client.post(reverse('auth:login'), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertEqual(response.context['error'], gettext('Email and password must be provided.'))


class SendEmailVerificationViewTest(TestCase):
    def setUp(self) -> None:
        self.user = CustomUser.objects.create_user(email="Ali@gmail.com",
                                                   password="salamsalam1")
        UserProfile.objects.create(user=self.user)
        self.client.login(email="Ali@gmail.com", password="salamsalam1")

    def test_request_with_wrong_method(self):
        response = self.client.get(reverse('auth:send-email-verification'))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content.decode(), 'Bad request (This url only accepts post requests)')

    def test_user_email_is_already_verified(self):
        self.user.is_email_verified = True
        self.user.save()
        response = self.client.post(reverse('auth:send-email-verification'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), 'Your email is already verified!')

    @patch('authentication.views.EmailMessage.send')
    def test_successful_request(self, mocked_send):
        response = self.client.post(reverse('auth:send-email-verification'), follow=True)

        self.assertEqual(response.status_code, 200)
        mocked_send.assert_called_once()


class VerifyEmailViewTest(TestCase):
    def setUp(self) -> None:
        self.user = CustomUser.objects.create_user(email="Ali@gmail.com",
                                                   password="salamsalam1")
        UserProfile.objects.create(user=self.user)
        self.user.refresh_verification_token()

    def test_request_with_invalid_token(self):
        wrong_token = get_random_string(50)

        response = self.client.get(reverse('auth:verify', kwargs={'token': wrong_token}))

        self.user.refresh_from_db()
        self.assertFalse(self.user.is_email_verified)
        self.assertEqual(response.content.decode(), 'Verification link is invalid!')

    def test_request_with_valid_credentials(self):
        correct_token = self.user.verification_token

        response = self.client.get(reverse('auth:verify',
                                           kwargs={'token': correct_token}),
                                   follow=True)

        self.user.refresh_from_db()
        self.assertTrue(self.user.is_email_verified)
        self.assertEqual(response.status_code, 200)


def create_profile(user, city, educational_level_list, skills):
    profile = UserProfile.objects.create(user=user, city_of_residence=city)
    profile.skills.set(skills)
    EducationalBackground.objects.bulk_create([
        EducationalBackground(user_profile=profile,
                              level=el,
                              start_year=2018,
                              finish_year=2020,
                              is_currently_studying=False)
        for el in educational_level_list])
    return profile


class TestQualifiedUsersForOffer(TestCase):
    def setUp(self) -> None:
        all_skills = Skill.objects.bulk_create([
            Skill(title='django'),
            Skill(title='docker'),
            Skill(title='.NET'),
            Skill(title='cpp')
        ])
        offer_skills = all_skills[1:]
        self.user = CustomUser.objects.create(email='user@email.com', password='ComplicatedPassword1')

        self.related_city = 'Isfahan'
        self.unrelated_city = 'Tehran'
        self.related_edu_level_list = [EducationalLevel.MASTERS_DEGREE, EducationalLevel.OTHERS]
        self.unrelated_edu_level_list = [EducationalLevel.ASSOCIATE, EducationalLevel.DIPLOMA]
        self.related_skills = all_skills
        self.unrelated_skills_one = offer_skills[1:]
        self.unrelated_skills_two = all_skills[:-1]

        self.offer = JobOffer.objects.create(
            company=Company.objects.create(name="CompanyName"),
            city=self.related_city,
            minimum_degree=EducationalLevel.BACHELORS_DEGREE,
        )
        self.offer.skills_required.set(offer_skills)

    def test_get_ge_educational_levels(self):
        self.assertEqual(set(EducationalLevel.BACHELORS_DEGREE.get_ge_educational_levels()),
                         {EducationalLevel.BACHELORS_DEGREE,
                          EducationalLevel.MASTERS_DEGREE,
                          EducationalLevel.DOCTORAL_DEGREE,
                          EducationalLevel.POSTDOCTORAL_DEGREE})

    def test_city_is_checked(self):
        create_profile(user=self.user,
                       city=self.unrelated_city,
                       educational_level_list=self.related_edu_level_list,
                       skills=self.related_skills)
        self.assertNotIn(self.user, CustomUser.objects.qualified_users_for_offer(self.offer))

    def test_educational_background_is_checked(self):
        create_profile(user=self.user,
                       city=self.related_city,
                       educational_level_list=self.unrelated_edu_level_list,
                       skills=self.related_skills)
        self.assertNotIn(self.user, CustomUser.objects.qualified_users_for_offer(self.offer))

    def test_skills_are_checked(self):
        create_profile(user=self.user,
                       city=self.related_city,
                       educational_level_list=self.related_edu_level_list,
                       skills=self.unrelated_skills_one)
        self.assertNotIn(self.user, CustomUser.objects.qualified_users_for_offer(self.offer))

        self.user.profile.delete()
        create_profile(user=self.user,
                       city=self.related_city,
                       educational_level_list=self.related_edu_level_list,
                       skills=self.unrelated_skills_two)
        self.assertNotIn(self.user, CustomUser.objects.qualified_users_for_offer(self.offer))

    def test_qualified_profile_for_offer(self):
        create_profile(user=self.user,
                       city=self.related_city,
                       educational_level_list=self.related_edu_level_list,
                       skills=self.related_skills)
        self.assertListEqual([self.user], list(CustomUser.objects.qualified_users_for_offer(self.offer)))
