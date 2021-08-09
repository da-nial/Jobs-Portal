from django.test import TestCase
from django.urls import reverse

from authentication.models import CustomUser


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
