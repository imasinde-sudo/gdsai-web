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

    def test_profile_page_redirects_anonymous_user(self):
        response = self.client.get(reverse('events:profile_view'))
        self.assertEqual(response.status_code, 302)

    def test_profile_page_accessible_by_staff_user(self):
        self.client.login(username="staff", password="password")
        response = self.client.get(reverse('events:profile_view'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Administrator Profile')

    def test_profile_update_submits_correctly(self):
        self.client.login(username="staff", password="password")
        post_data = {
            "first_name": "NewFirstName",
            "last_name": "NewLastName",
            "email": "updatedadmin@eventhub.com"
        }
        response = self.client.post(reverse('events:profile_view'), post_data)
        self.assertEqual(response.status_code, 302)
        
        # Verify database fields updated
        self.staff_user.refresh_from_db()
        self.assertEqual(self.staff_user.first_name, "NewFirstName")
        self.assertEqual(self.staff_user.last_name, "NewLastName")
        self.assertEqual(self.staff_user.email, "updatedadmin@eventhub.com")


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
        # Response is paginated — results are under the 'results' key
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["title"], "AI Summit")

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

    def test_api_schema_endpoint(self):
        response = self.client.get(reverse('events:api_schema'))
        self.assertEqual(response.status_code, 200)
        self.assertIn("openapi", response.json())


class MobileAPIv1Tests(TestCase):
    """
    Tests for the public mobile API v1 endpoints.
    No authentication is required for these endpoints.
    """
    def setUp(self):
        from .models import Speaker
        self.speaker = Speaker.objects.create(
            name="Jane Doe",
            title="AI Researcher",
            organization="Agentic Labs",
        )
        self.event = Event.objects.create(
            title="Global Tech Summit",
            description="Annual tech conference.",
            start_date="2026-07-15T09:00:00Z",
            end_date="2026-07-17T17:00:00Z",
            location="Nairobi Convention Centre",
        )
        self.session = Session.objects.create(
            event=self.event,
            title="Opening Keynote",
            description="Kickoff session.",
            start_time="2026-07-15T09:00:00Z",
            end_time="2026-07-15T10:30:00Z",
            location="Auditorium A",
        )
        self.session.speakers.add(self.speaker)

    # --- Event Endpoints ---

    def test_v1_event_list_returns_200(self):
        response = self.client.get(reverse('events:v1_event_list'))
        self.assertEqual(response.status_code, 200)

    def test_v1_event_list_includes_sessions_count(self):
        response = self.client.get(reverse('events:v1_event_list'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('results', data)  # Paginated response
        self.assertEqual(data['results'][0]['sessions_count'], 1)

    def test_v1_event_detail_returns_correct_event(self):
        response = self.client.get(reverse('events:v1_event_detail', kwargs={'pk': self.event.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['title'], 'Global Tech Summit')

    def test_v1_event_detail_returns_404_for_invalid_id(self):
        response = self.client.get(reverse('events:v1_event_detail', kwargs={'pk': 9999}))
        self.assertEqual(response.status_code, 404)

    def test_v1_event_sessions_returns_sessions_for_event(self):
        response = self.client.get(reverse('events:v1_event_sessions', kwargs={'event_id': self.event.id}))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('results', data)
        self.assertEqual(data['results'][0]['title'], 'Opening Keynote')

    def test_v1_event_sessions_returns_404_for_invalid_event(self):
        response = self.client.get(reverse('events:v1_event_sessions', kwargs={'event_id': 9999}))
        self.assertEqual(response.status_code, 404)

    # --- Speaker Endpoints ---

    def test_v1_speaker_list_returns_200(self):
        response = self.client.get(reverse('events:v1_speaker_list'))
        self.assertEqual(response.status_code, 200)

    def test_v1_speaker_detail_returns_correct_speaker(self):
        response = self.client.get(reverse('events:v1_speaker_detail', kwargs={'pk': self.speaker.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['name'], 'Jane Doe')

    # --- Session Endpoints ---

    def test_v1_session_detail_returns_correct_session(self):
        response = self.client.get(reverse('events:v1_session_detail', kwargs={'pk': self.session.id}))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['title'], 'Opening Keynote')
        self.assertEqual(len(data['speakers']), 1)
        self.assertEqual(data['speakers'][0]['name'], 'Jane Doe')

    # --- Q&A Endpoints ---

    def test_v1_questions_list_for_session(self):
        Question.objects.create(session=self.session, text="What is an AI agent?")
        response = self.client.get(
            reverse('events:v1_session_questions', kwargs={'session_id': self.session.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]['text'], 'What is an AI agent?')

    def test_v1_question_submission_creates_record(self):
        response = self.client.post(
            reverse('events:v1_session_questions', kwargs={'session_id': self.session.id}),
            {"text": "How do I build a mobile app?"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Question.objects.count(), 1)
        self.assertEqual(Question.objects.first().text, 'How do I build a mobile app?')

    def test_v1_question_submission_requires_text(self):
        response = self.client.post(
            reverse('events:v1_session_questions', kwargs={'session_id': self.session.id}),
            {},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())
