from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Event, APIKey, Session, Question

class AdminSecurityTests(TestCase):
    def setUp(self):
        self.staff_user = User.objects.create_user(username="staff", password="password", is_staff=True)
        self.regular_user = User.objects.create_user(username="user", password="password")

    def test_dashboard_redirects_anonymous_user(self):
        response = self.client.get(reverse('events:admin_dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/login/'))

    def test_system_status_redirects_anonymous_user(self):
        response = self.client.get(reverse('events:system_status'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/login/'))

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

    def test_login_page_renders_form(self):
        response = self.client.get(reverse('events:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id_username')
        self.assertContains(response, 'id_password')

    def test_login_view_authenticates_correctly(self):
        post_data = {
            "username": "staff",
            "password": "password"
        }
        response = self.client.post(reverse('events:login'), post_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.endswith('/dashboard/'))

    def test_login_view_invalid_credentials_returns_error(self):
        post_data = {
            "username": "staff",
            "password": "wrongpassword"
        }
        response = self.client.post(reverse('events:login'), post_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid username or password')


class RESTAPITests(TestCase):
    def setUp(self):
        self.apikey = APIKey.objects.create(name="Test Key")
        self.event = Event.objects.create(
            title="AI Summit",
            description="Deep learning event",
            start_date="2026-07-15T09:00:00Z",
            end_date="2026-07-15T17:00:00Z",
            location="Nakuru"
        )
        self.session = Session.objects.create(
            event=self.event,
            title="Introduction to LLMs",
            description="LLM tutorial description",
            start_time="2026-07-15T10:00:00Z",
            end_time="2026-07-15T11:00:00Z",
            location="Kawi Room 2"
        )

    def test_api_requires_api_key(self):
        response = self.client.get(reverse('events:api_events'))
        self.assertEqual(response.status_code, 403)
        self.assertIn("API key is required", response.data["detail"])

    def test_api_denies_invalid_api_key(self):
        response = self.client.get(reverse('events:api_events'), HTTP_X_API_KEY="invalidtoken")
        self.assertEqual(response.status_code, 403)
        self.assertIn("Invalid or inactive API key", response.data["detail"])

    def test_api_grants_access_with_valid_key(self):
        response = self.client.get(reverse('events:api_events'), HTTP_X_API_KEY=self.apikey.key)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "AI Summit")

    def test_session_question_submission(self):
        # Questions submission is public, doesn't require key
        post_data = {"text": "How do we finetune this LLM?"}
        response = self.client.post(
            reverse('events:api_session_questions', kwargs={"session_id": self.session.id}),
            post_data,
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Question.objects.count(), 1)
        self.assertEqual(Question.objects.first().text, "How do we finetune this LLM?")

        # Test listing questions for this session
        get_response = self.client.get(
            reverse('events:api_session_questions', kwargs={"session_id": self.session.id})
        )
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(len(get_response.data), 1)
        self.assertEqual(get_response.data[0]["text"], "How do we finetune this LLM?")


