import json
import pytest
from model import db, User, Lesson
from werkzeug.security import generate_password_hash
from datetime import datetime
import uuid

# --- Fixtures for User and Token ---

@pytest.fixture
def test_user(session):
    """Creates and returns a unique user instance for each test."""
    unique_id = uuid.uuid4().hex[:8]
    password = "password123"
    user = User(email=f"lesson_user_{unique_id}@example.com", username=f"lesson_user_{unique_id}", password_hash=generate_password_hash(password))
    session.add(user)
    session.flush()
    return user, password

@pytest.fixture
def test_user_token(client, test_user):
    """Logs in the test user via the API and returns a valid token."""
    user, password = test_user
    response = client.post('/api/login', data=json.dumps({'username': user.username, 'password': password}), content_type='application/json')
    assert response.status_code == 200, f"Login failed for test user: {response.get_data(as_text=True)}"
    data = response.get_json()
    return data['access_token']

# --- Tests for Lesson Endpoints ---

def test_get_all_lessons_success(client, session, test_user_token):
    """
    GIVEN a logged-in user and existing lessons in the database
    WHEN the '/api/get_all_lessons' endpoint is accessed
    THEN check that a 200 status code is returned with a list of all lessons
    """
    # Clean the table for an isolated test environment
    session.query(Lesson).delete()
    
    # Seed the database with some lessons
    lesson1 = Lesson(lesson_name="Introduction to Budgeting", lesson_description="Learn the basics of creating and sticking to a budget.")
    lesson2 = Lesson(lesson_name="Understanding the Stock Market", lesson_description="A beginner's guide to stocks and investing.")
    session.add_all([lesson1, lesson2])
    session.flush()

    headers = {'Authorization': f'Bearer {test_user_token}'}
    response = client.get('/api/get_all_lessons', headers=headers)

    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    
    lesson_names = {item['lesson_name'] for item in data}
    assert "Introduction to Budgeting" in lesson_names
    assert "Understanding the Stock Market" in lesson_names

def test_get_all_lessons_no_lessons(client, session, test_user_token):
    """
    GIVEN a logged-in user but no lessons in the database
    WHEN the '/api/get_all_lessons' endpoint is accessed
    THEN check that a 200 status code is returned with an empty list
    """
    # Ensure the Lesson table is empty for this test
    session.query(Lesson).delete()
    session.flush()

    headers = {'Authorization': f'Bearer {test_user_token}'}
    response = client.get('/api/get_all_lessons', headers=headers)

    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 0

def test_get_all_lessons_no_token(client):
    """
    GIVEN a request to the '/api/get_all_lessons' endpoint without an authentication token
    WHEN the endpoint is accessed
    THEN check that a 401 Unauthorized status code is returned
    """
    response = client.get('/api/get_all_lessons')
    assert response.status_code == 401
