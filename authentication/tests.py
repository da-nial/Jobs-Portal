from unittest.mock import patch
from django.utils.crypto import get_random_string
from django.test import TestCase
from django.urls import reverse
from authentication.models import CustomUser
from jobs.models import UserProfile


class LoginViewTest(TestCase):
    def setUp(self) -> None:
        super().setUp()

        user = CustomUser.objects.create(email='sara@gmail.com', is_active=True)
        user.set_password('salamsalam1')
        user.save()

    def test_successful_login(self):
        data = {'email': 'sara@gmail.com', 'password': 'salamsalam1'}
        response = self.client.post(reverse('auth:login'), data=data)
        self.assertEqual(response.status_code, 200)

    def test_wrong_password(self):
        data = {'email': 'sara@gmail.com', 'password': 'sadsad'}
        response = self.client.post(reverse('auth:login'), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertEqual(response.context['error'], 'Wrong credentials.')

    def test_wrong_email(self):
        data = {'email': 'sara1@gmail.com', 'password': 'salamsalam1'}
        response = self.client.post(reverse('auth:login'), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertEqual(response.context['error'], 'Wrong credentials.')

    def test_password_is_empty(self):
        data = {'email': 'sara@gmail.com'}
        response = self.client.post(reverse('auth:login'), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertEqual(response.context['error'], 'Email and password must be provided.')

    def test_email_is_empty(self):
        data = {'password': 'salamsalam1'}
        response = self.client.post(reverse('auth:login'), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertEqual(response.context['error'], 'Email and password must be provided.')


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
