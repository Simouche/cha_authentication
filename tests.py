from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

from authentication.models import MultiToken

User = get_user_model()


class AuthenticationTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.login_url = reverse('login')

    def test_login(self):
        data = {
            'username': 'testuser',
            'password': 'testpassword'
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)


class CheckAuthTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        self.check_auth_url = reverse('check_login')

    def test_check_auth(self):
        response = self.client.get(self.check_auth_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['connected'])


class LogoutTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.token = MultiToken.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.logout_url = reverse('logout')

    def test_logout(self):
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(MultiToken.objects.filter(key=self.token.key).exists())


# class RequestPasswordResetTests(APITestCase):
#
#     def setUp(self):
#         self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
#         self.request_reset_url = reverse('request_reset_password')
#
#     def test_request_password_reset(self):
#         data = {
#             'email': 'test@example.com'
#         }
#         response = self.client.post(self.request_reset_url, data, format='json')
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.data['details'], 'Password reset requested.')

# class ResetPasswordTests(APITestCase):
#
#     def setUp(self):
#         self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
#         self.verification = Verification.objects.create(email='test@example.com')
#         self.reset_password_url = reverse('reset-password')
#
#     def test_reset_password(self):
#         data = {
#             'otp': self.verification.otp,
#             'password': 'newpassword',
#             'confirm_password': 'newpassword'
#         }
#         response = self.client.post(self.reset_password_url, data, format='json')
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.data['details'], 'Password reset successfully')
