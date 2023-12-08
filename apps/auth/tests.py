from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from .models import UserProfile

class AuthModelTest(TestCase):
    def setUp(self):
        self.credentials = {
            'username': 'testuser',
            'password': 'testpassword',
        }
        self.user = User.objects.create_user(**self.credentials)
        self.profile = UserProfile.objects.create(user=self.user, type='user')
        
    def test_sign_up_admin(self):
        response = self.client.post(reverse('auth:sign_up'), {
            'username': 'newadmin',
            'password1': 'newpassword1',
            'password2': 'newpassword1',
            'key': 'admin',
        })
        self.assertEqual(response.status_code, 302)
        admin = User.objects.get(username='newadmin')
        self.assertIsNotNone(admin)
        admin_profile = UserProfile.objects.get(user__username='newadmin')
        self.assertIsNotNone(admin_profile)
        self.assertEqual(admin_profile.type, 'admin')
        
    def test_sign_up_user(self):
        response = self.client.post(reverse('auth:sign_up'), {
            'username': 'newuser',
            'password1': 'newpassword1',
            'password2': 'newpassword1',
            'key': 'user',
        })
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='newuser')
        self.assertIsNotNone(user)
        user_profile = UserProfile.objects.get(user__username='newuser')
        self.assertIsNotNone(user_profile)
        self.assertEqual(user_profile.type, 'user')
        
    def test_sign_in_user(self):
        response = self.client.post(reverse('auth:sign_in'), self.credentials, follow=True)
        self.assertTrue(response.context['user'].is_authenticated)
        
    def test_sign_in_user_with_remember_me(self):
        response = self.client.post(reverse('auth:sign_in'), {**self.credentials, 'remember-me': 'on'}, follow=True)
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertEqual(response.client.session.get_expiry_age(), 2592000)
        
    def test_sign_in_invalid_user(self):
        response = self.client.post(reverse('auth:sign_in'), {'username': 'invalid', 'password': 'invalid'}, follow=True)
        self.assertFalse(response.context['user'].is_authenticated)
        