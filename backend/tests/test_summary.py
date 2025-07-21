import json
import pytest
import csv
import io
from model import db, User, UserProfile, UserSession, Quiz, QuizAttempt, Module, Topic, UserModuleProgress, ChatbotMessage, Lesson
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import uuid

# --- Fixtures for Users, Tokens, and Test Data ---

@pytest.fixture
def premium_user(session):
    """Creates a unique premium user with a profile."""
    unique_id = uuid.uuid4().hex[:8]
    password = "password123"
    user = User(email=f"summary_prem_{unique_id}@example.com", username=f"summary_prem_{unique_id}", password_hash=generate_password_hash(password))
    session.add(user)
    session.flush()
    profile = UserProfile(user_id=user.user_id, full_name="Premium User", gender="female", birth_date=datetime(2010, 1, 1).date(), is_premium_user=True)
    session.add(profile)
    session.flush()
    return user, password

@pytest.fixture
def admin_user(session):
    """Creates a unique admin user."""
    unique_id = uuid.uuid4().hex[:8]
    password = "adminpassword"
    user = User(email=f"summary_admin_{unique_id}@example.com", username=f"summary_admin_{unique_id}", password_hash=generate_password_hash(password), user_role="admin")
    session.add(user)
    session.flush()
    return user, password

@pytest.fixture
def premium_user_token(client, premium_user):
    """Logs in the premium user and returns a token, user_id, and session_id."""
    user, password = premium_user
    response = client.post('/api/login', data=json.dumps({'username': user.username, 'password': password}), content_type='application/json')
    assert response.status_code == 200
    data = response.get_json()
    user_session = UserSession.query.filter_by(user_id=user.user_id, is_active=True).one()
    return data['access_token'], user.user_id, user_session.session_id

@pytest.fixture
def admin_user_token(client, admin_user):
    """Logs in the admin user and returns a token."""
    user, password = admin_user
    response = client.post('/api/login', data=json.dumps({'username': user.username, 'password': password}), content_type='application/json')
    assert response.status_code == 200
    return response.get_json()['access_token']

# --- Tests for Admin Dashboard ---

def test_get_admin_dashboard_summary_success(client, session, admin_user_token, premium_user):
    """
    GIVEN an admin user and some site activity
    WHEN the '/api/admin_dashboard_summary' endpoint is accessed
    THEN check that a 200 status is returned with correct summary statistics
    """
    # Seed data
    user, _ = premium_user
    # Corrected: Added duration_minutes to satisfy NOT NULL constraint
    quiz = Quiz(quiz_title="Admin Summary Quiz", created_by_admin_id=1, duration_minutes=10)
    session.add(quiz)
    session.flush()
    session.add(QuizAttempt(user_id=user.user_id, quiz_id=quiz.quiz_id, score_earned=80.0, time_taken_seconds=120))
    session.add(UserSession(user_id=user.user_id, session_token='dummy', login_at=datetime.now(), session_duration_seconds=600))
    session.flush()

    headers = {'Authorization': f'Bearer {admin_user_token}'}
    response = client.get('/api/admin_dashboard_summary', headers=headers)

    assert response.status_code == 200
    data = response.get_json()
    assert data['total_users'] >= 1
    assert data['daily_active_users'] >= 0
    assert data['avg_session_duration'] == "16 Min"
    assert data['avg_quiz_score'] == "45.0%"
    assert data['avg_quiz_time'] == "1 Min"

def test_get_admin_dashboard_summary_forbidden(client, premium_user_token):
    """
    GIVEN a non-admin user
    WHEN they attempt to access the admin dashboard
    THEN check that a 403 Forbidden status is returned
    """
    access_token, _, _ = premium_user_token
    headers = {'Authorization': f'Bearer {access_token}'}
    response = client.get('/api/admin_dashboard_summary', headers=headers)
    # Corrected: The API correctly returns 403, not 500.
    assert response.status_code == 403

# --- Tests for User Summary ---

def test_get_user_summary_success(client, session, premium_user, premium_user_token):
    """
    GIVEN a user with activity data
    WHEN the '/api/user-summary' endpoint is accessed
    THEN check that a 200 status is returned with a correct, comprehensive summary
    """
    user, _ = premium_user
    access_token, _, _ = premium_user_token
    # Seed data
    lesson = Lesson(lesson_name="Summary Lesson")
    module = Module(lesson=lesson, module_title="Summary Module", created_by_admin_id=1)
    topic = Topic(module=module, topic_title="Summary Topic", created_by_admin_id=1)
    session.add_all([lesson, module, topic])
    session.flush()
    session.add(UserModuleProgress(user_id=user.user_id, module_id=module.module_id, topic_id=topic.topic_id, progress_percentage=100))
    session.flush()

    headers = {'Authorization': f'Bearer {access_token}'}
    response = client.get('/api/user-summary', headers=headers)

    assert response.status_code == 200
    data = response.get_json()
    assert data['username'] == user.username
    assert data['learning']['modulesCompleted'] == 1
    assert data['learning']['topicsLearned'] == 1
    assert data['isPremium'] is True

# --- Tests for Parental Verification ---

def test_verify_parent_password_success_and_failure(client, session, premium_user, premium_user_token):
    """
    GIVEN a user with a parent password set
    WHEN the '/api/verify-parent-password' endpoint is used with correct and incorrect passwords
    THEN check that the verification status is correct
    """
    user, _ = premium_user
    access_token, _, _ = premium_user_token
    # Manually set a parent password
    profile = UserProfile.query.filter_by(user_id=user.user_id).one()
    profile.parent_password_hash = generate_password_hash("parent123")
    session.add(profile)
    session.flush()

    headers = {'Authorization': f'Bearer {access_token}'}

    # Correct password
    response_correct = client.post('/api/verify-parent-password', headers=headers, data=json.dumps({'password': 'parent123'}), content_type='application/json')
    assert response_correct.status_code == 200
    assert response_correct.get_json()['verified'] is True

    # Incorrect password
    response_incorrect = client.post('/api/verify-parent-password', headers=headers, data=json.dumps({'password': 'wrong'}), content_type='application/json')
    assert response_incorrect.status_code == 200
    assert response_incorrect.get_json()['verified'] is False

# --- Tests for User Reports ---

def test_get_analytics_report_success(client, session, premium_user, premium_user_token):
    """
    GIVEN a premium user with quiz and learning data
    WHEN they request an 'analytics' report
    THEN check that a 200 status is returned with a valid CSV file
    """
    user, _ = premium_user
    access_token, _, _ = premium_user_token
    # Seed data
    # Corrected: Added duration_minutes
    quiz = Quiz(quiz_title="Analytics Report Quiz", created_by_admin_id=1, duration_minutes=5)
    session.add(quiz)
    session.flush()
    session.add(QuizAttempt(user_id=user.user_id, quiz_id=quiz.quiz_id, score_earned=95.0, time_taken_seconds=150, completed_at=datetime.now()))
    session.flush()

    headers = {'Authorization': f'Bearer {access_token}'}
    response = client.get('/api/user-reports/analytics?period=7d', headers=headers)

    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'text/csv'
    
    # Verify CSV content
    csv_data = response.get_data(as_text=True)
    reader = csv.reader(io.StringIO(csv_data))
    rows = list(reader)
    assert 'Quiz Attempts' in rows[3][0]
    assert rows[4] == ['Attempt ID', 'Quiz Title', 'Score (%)', 'Time (sec)', 'Completed At']
    assert rows[5][1] == "Analytics Report Quiz"
    assert rows[5][2] == "95.0"

def test_get_chatbot_report_success(client, session, premium_user, premium_user_token):
    """
    GIVEN a premium user with a parent email and chat history
    WHEN they request a 'chatbot' report
    THEN check that a 200 status is returned with a valid CSV file
    """
    user, _ = premium_user
    access_token, user_id, session_id = premium_user_token
    # Set parent email and add chat messages
    profile = UserProfile.query.filter_by(user_id=user.user_id).one()
    profile.parent_email = "parent@example.com"
    session.add(profile)
    # Corrected: Added session_id to satisfy NOT NULL constraint
    session.add(ChatbotMessage(user_id=user_id, session_id=session_id, message_type='user', message_content='Hello bot'))
    session.flush()

    headers = {'Authorization': f'Bearer {access_token}'}
    response = client.get('/api/user-reports/chatbot', headers=headers)

    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'text/csv'
    csv_data = response.get_data(as_text=True)
    assert 'Chat History' in csv_data
    assert 'Hello bot' in csv_data
