from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Event

class AdminSecurityTests(TestCase):
    def setUp(self):
        self.staff_user = User.objects.create_user(username="staff", password="password", is_staff=True)
        self.regular_user = User.objects.create_user(username="user", password="password")

    def test_dashboard_redirects_anonymous_user(self):
        response = self.client.get(reverse('events:admin_dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/admin/login/'))

    def test_system_status_redirects_anonymous_user(self):
        response = self.client.get(reverse('events:system_status'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/admin/login/'))

    def test_event_create_redirects_anonymous_user(self):
        response = self.client.get(reverse('events:event_create'))
        self.assertEqual(response.status_code, 302)

    def test_event_create_by_staff_user(self):
        self.client.login(username="staff", password="password")
        post_data = {
            "title": "New Event Testing",
            "description": "Short description",
            "start_date": "2026-07-10T10:00",
            "end_date": "2026-07-10T12:00",
            "location": "Auditorium A"
        }
        response = self.client.post(reverse('events:event_create'), post_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Event.objects.count(), 1)
        self.assertEqual(Event.objects.first().title, "New Event Testing")

