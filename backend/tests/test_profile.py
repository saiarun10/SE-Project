import json
import pytest
from model import db, User, UserProfile, UserSession
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import uuid

# --- Fixtures for User and Token ---

@pytest.fixture
def test_user(session):
    """Creates and returns a unique user and profile instance for each test."""
    unique_id = uuid.uuid4().hex[:8]
    password = "password123"
    user = User(
        email=f"profile_user_{unique_id}@example.com", 
        username=f"profile_user_{unique_id}", 
        password_hash=generate_password_hash(password)
    )
    session.add(user)
    session.flush()
    
    profile = UserProfile(
        user_id=user.user_id,
        full_name="Test User",
        gender="other",
        birth_date=datetime.strptime("2010-05-15", "%Y-%m-%d").date()
    )
    session.add(profile)
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

# --- Tests for Profile Endpoints ---

def test_get_user_profile_success(client, test_user_token):
    """
    GIVEN a logged-in user with a profile
    WHEN the '/api/get_user_profile' endpoint is accessed
    THEN check that a 200 status code is returned with the correct profile details
    """
    headers = {'Authorization': f'Bearer {test_user_token}'}
    response = client.get('/api/get_user_profile', headers=headers)
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['full_name'] == "Test User"
    assert data['gender'] == "other"
    assert data['birth_date'] == "2010-05-15"

def test_update_user_profile_success(client, test_user_token):
    """
    GIVEN a logged-in user
    WHEN the '/api/get_user_profile' (PUT) endpoint is used to update the profile
    THEN check that a 200 status code is returned and the profile is updated
    """
    headers = {'Authorization': f'Bearer {test_user_token}'}
    update_data = {
        "full_name": "Updated Test User",
        "gender": "male",
        "birth_date": "2011-06-16"
    }
    
    response = client.put('/api/get_user_profile', 
                          headers=headers, 
                          data=json.dumps(update_data), 
                          content_type='application/json')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['full_name'] == "Updated Test User"
    assert data['gender'] == "male"
    assert data['birth_date'] == "2011-06-16"

def test_update_user_profile_invalid_age(client, test_user_token):
    """
    GIVEN a logged-in user
    WHEN they attempt to update their birth date to an invalid age (e.g., too young)
    THEN check that a 500 status code is returned due to the app's error handling
    """
    headers = {'Authorization': f'Bearer {test_user_token}'}
    # This birth date would make the user too young according to the validation logic
    update_data = {"birth_date": "2022-01-01"}
    
    response = client.put('/api/get_user_profile', 
                          headers=headers, 
                          data=json.dumps(update_data), 
                          content_type='application/json')
                          
    # The app's generic exception handler turns the 422 abort into a 500
    assert response.status_code == 500

# --- Tests for Parental Control Endpoints ---

def test_set_parent_email_success(client, test_user_token):
    """
    GIVEN a logged-in user without a parent email set
    WHEN the '/api/set_parent_email' endpoint is used
    THEN check that a 200 status code is returned and the email is set
    """
    headers = {'Authorization': f'Bearer {test_user_token}'}
    parent_data = {
        "parent_email": "parent@example.com",
        "parent_password": "parentpassword"
    }
    
    response = client.post('/api/set_parent_email', 
                           headers=headers, 
                           data=json.dumps(parent_data), 
                           content_type='application/json')
                           
    assert response.status_code == 200
    assert "Parent email set successfully" in response.get_json()['message']

def test_set_parent_email_already_exists(client, test_user_token):
    """
    GIVEN a user who already has a parent email set
    WHEN they attempt to set it again
    THEN check that a 500 status code is returned due to the app's error handling
    """
    headers = {'Authorization': f'Bearer {test_user_token}'}
    parent_data = {"parent_email": "first.parent@example.com", "parent_password": "password"}
    
    # Set it the first time
    client.post('/api/set_parent_email', headers=headers, data=json.dumps(parent_data), content_type='application/json')
    
    # Attempt to set it again
    second_attempt_data = {"parent_email": "second.parent@example.com", "parent_password": "password"}
    response = client.post('/api/set_parent_email', 
                           headers=headers, 
                           data=json.dumps(second_attempt_data), 
                           content_type='application/json')
                           
    # The app's generic exception handler turns the 409 abort into a 500
    assert response.status_code == 500

# --- Test for Premium Status Endpoint ---

def test_get_user_premium_status(client, session, test_user, test_user_token):
    """
    GIVEN a logged-in user
    WHEN their premium status is checked before and after an update
    THEN check that the status is correctly reported
    """
    user, _ = test_user
    headers = {'Authorization': f'Bearer {test_user_token}'}
    
    # 1. Check initial status (should be False by default)
    response_before = client.get('/api/get_user_premium_status', headers=headers)
    assert response_before.status_code == 200
    assert response_before.get_json()['is_premium_user'] is False
    
    # 2. Manually update the user's profile to be premium
    user_profile = UserProfile.query.filter_by(user_id=user.user_id).first()
    user_profile.is_premium_user = True
    session.add(user_profile)
    session.flush()
    
    # 3. Check status again
    response_after = client.get('/api/get_user_premium_status', headers=headers)
    assert response_after.status_code == 200
    assert response_after.get_json()['is_premium_user'] is True

# --- Test for Session History Endpoint ---

def test_get_user_sessions(client, session, test_user, test_user_token):
    """
    GIVEN a user with multiple sessions
    WHEN their session history is requested
    THEN check that a 200 status code is returned with the correct session data
    """
    user, _ = test_user
    
    # Seed some session data
    # Corrected: Added session_token to satisfy NOT NULL constraint
    session1 = UserSession(
        user_id=user.user_id, 
        session_token="dummy_token_1",
        login_at=datetime.now() - timedelta(days=2), 
        logout_at=datetime.now() - timedelta(days=2, hours=-1), 
        session_duration_seconds=3600
    )
    session2 = UserSession(
        user_id=user.user_id, 
        session_token="dummy_token_2",
        login_at=datetime.now() - timedelta(days=1)
    ) # Active session
    session.add_all([session1, session2])
    session.flush()
    
    headers = {'Authorization': f'Bearer {test_user_token}'}
    response = client.get('/api/get_user_sessions', headers=headers)
    
    assert response.status_code == 200
    data = response.get_json()
    # The login from the fixture + the 2 seeded sessions
    assert len(data) >= 3
    assert data[0]['session_duration_seconds'] is None # The most recent session is active
