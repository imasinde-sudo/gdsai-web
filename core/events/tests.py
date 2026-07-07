from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

class AdminSecurityTests(TestCase):
    def test_dashboard_redirects_anonymous_user(self):
        response = self.client.get(reverse('events:admin_dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/admin/login/'))

    def test_system_status_redirects_anonymous_user(self):
        response = self.client.get(reverse('events:system_status'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/admin/login/'))
