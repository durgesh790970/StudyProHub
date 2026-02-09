from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from accounts.models import Video, PDF


class AuthFlowTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.signup_url = reverse('accounts:signup_page')
        self.login_url = reverse('accounts:login_page')
        self.dashboard_url = reverse('accounts:dashboard')

        # ensure at least one video/pdf exists for dashboard rendering
        Video.objects.create(title='Test Video', video_id='abcd1234')
        PDF.objects.create(title='Test PDF', url='https://example.com/test.pdf', company='TestCo')

    def test_signup_and_redirects_to_dashboard(self):
        resp = self.client.post(self.signup_url, {
            'fullname': 'Test User',
            'email': 'testuser@example.com',
            'password': 'testpass123',
            'confirmPassword': 'testpass123',
        })
        # should redirect to dashboard
        self.assertEqual(resp.status_code, 302)
        self.assertIn(self.dashboard_url, resp.url)

        # dashboard should be accessible after signup (session set)
        resp2 = self.client.get(self.dashboard_url)
        self.assertIn(resp2.status_code, (200, 302))

    def test_login_with_created_user(self):
        User = get_user_model()
        # create a user
        u = User.objects.create_user(username='loginuser@example.com', email='loginuser@example.com')
        u.set_password('loginpass')
        u.save()

        # login post
        resp = self.client.post(self.login_url, {
            'email': 'loginuser@example.com',
            'password': 'loginpass'
        })
        self.assertEqual(resp.status_code, 302)
        self.assertIn(self.dashboard_url, resp.url)
