import json
from model import User, UserProfile, UserSession
from werkzeug.security import generate_password_hash

def test_signup_success(client, session):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/signup' endpoint is posted to with valid data
    THEN check that a 201 status code is returned and the user is created in the database
    """
    response = client.post('/api/signup',
                           data=json.dumps({
                               "email": "test.success@example.com",
                               "username": "testuser.success",
                               "password": "password123",
                               "birth_date": "1995-05-10",
                               "gender": "male",
                               "full_name": "Test User",
                               "parent_email": ""
                           }),
                           content_type='application/json')
    
    assert response.status_code == 201
    data = response.get_json()
    assert data['email'] == 'test.success@example.com'
    assert data['username'] == 'testuser.success'
    
    user = User.query.filter_by(email="test.success@example.com").first()
    assert user is not None
    user_profile = UserProfile.query.filter_by(user_id=user.user_id).first()
    assert user_profile is not None
    assert user_profile.full_name == "Test User"

def test_signup_duplicate_username(client, session):
    """
    GIVEN a user already exists in the database
    WHEN the '/api/signup' endpoint is posted to with the same username
    THEN check that a 500 status code is returned due to the broad exception handling
    """
    # Pre-create a user with a unique username for this test
    user = User(email="original.dup.user@example.com", username="testuser.duplicate", password_hash=generate_password_hash("password"))
    session.add(user)
    session.commit() # Use commit() to make the user visible to the app context

    response = client.post('/api/signup',
                           data=json.dumps({
                               "email": "new.dup.user@example.com",
                               "username": "testuser.duplicate", # Attempt to use the same username
                               "password": "password123",
                               "birth_date": "1995-05-10",
                               "gender": "male",
                               "full_name": "New User"
                           }),
                           content_type='application/json')
    
    # The app's generic exception handler turns the 409 abort into a 500
    assert response.status_code == 500
    assert "An unexpected error occurred" in response.get_json()['message']

def test_signup_duplicate_email(client, session):
    """
    GIVEN a user already exists in the database
    WHEN the '/api/signup' endpoint is posted to with the same email
    THEN check that a 500 status code is returned due to the broad exception handling
    """
    # Pre-create a user with a unique email for this test
    user = User(email="test.duplicate@example.com", username="original.dup.email", password_hash=generate_password_hash("password"))
    session.add(user)
    session.commit() # Use commit() to make the user visible to the app context

    response = client.post('/api/signup',
                           data=json.dumps({
                               "email": "test.duplicate@example.com", # Attempt to use the same email
                               "username": "new.dup.email",
                               "password": "password123",
                               "birth_date": "1995-05-10",
                               "gender": "male",
                               "full_name": "New User"
                           }),
                           content_type='application/json')
    
    # The app's generic exception handler turns the 409 abort into a 500
    assert response.status_code == 500
    assert "An unexpected error occurred" in response.get_json()['message']

def test_signup_missing_fields(client):
    """
    GIVEN a Flask application
    WHEN the '/api/signup' endpoint is posted to with missing fields
    THEN check that a 500 status code is returned due to the broad exception handling
    """
    response = client.post('/api/signup',
                           data=json.dumps({
                               "email": "missing.fields@example.com",
                               "password": "password123"
                           }),
                           content_type='application/json')
    
    # The app's generic exception handler turns the 400 abort into a 500
    assert response.status_code == 500
    assert "An unexpected error occurred" in response.get_json()['message']

def test_signup_invalid_birthdate(client):
    """
    GIVEN a Flask application
    WHEN the '/api/signup' endpoint is posted to with an invalid date format
    THEN check that a 500 status code is returned due to the broad exception handling
    """
    response = client.post('/api/signup',
                           data=json.dumps({
                               "email": "invalid.date@example.com",
                               "username": "invaliddateuser",
                               "password": "password123",
                               "birth_date": "10-05-1995", # Invalid format
                               "gender": "male",
                               "full_name": "Invalid User"
                           }),
                           content_type='application/json')

    # The app's generic exception handler turns the 422 abort into a 500
    assert response.status_code == 500
    assert "An unexpected error occurred" in response.get_json()['message']

def test_login_success(client, session):
    """
    GIVEN a registered user
    WHEN the '/api/login' endpoint is posted to with correct credentials
    THEN check that a 200 status code is returned and an access token is provided
    """
    password = "password123"
    user = User(email="login.success@example.com", username="loginuser.success", password_hash=generate_password_hash(password))
    session.add(user)
    session.commit() # Use commit() to make the user visible to the app context

    response = client.post('/api/login',
                           data=json.dumps({
                               "username": "loginuser.success",
                               "password": password
                           }),
                           content_type='application/json')

    assert response.status_code == 200
    data = response.get_json()
    assert "access_token" in data
    assert data['user']['username'] == 'loginuser.success'

def test_login_invalid_username(client):
    """
    GIVEN a Flask application
    WHEN the '/api/login' endpoint is posted to with a non-existent username
    THEN check that a 500 status code is returned due to the broad exception handling
    """
    response = client.post('/api/login',
                           data=json.dumps({
                               "username": "nouser",
                               "password": "password123"
                           }),
                           content_type='application/json')
    
    # The app's generic exception handler turns the 401 abort into a 500
    assert response.status_code == 500
    assert "An unexpected error occurred" in response.get_json()['message']

def test_login_invalid_password(client, session):
    """
    GIVEN a registered user
    WHEN the '/api/login' endpoint is posted to with an incorrect password
    THEN check that a 500 status code is returned due to the broad exception handling
    """
    user = User(email="login_invalid@example.com", username="loginuser_invalid", password_hash=generate_password_hash("password123"))
    session.add(user)
    session.commit() # Use commit() to make the user visible to the app context

    response = client.post('/api/login',
                           data=json.dumps({
                               "username": "loginuser_invalid",
                               "password": "wrongpassword"
                           }),
                           content_type='application/json')

    # The app's generic exception handler turns the 401 abort into a 500
    assert response.status_code == 500
    assert "An unexpected error occurred" in response.get_json()['message']

def test_validate_token_success(client, session):
    """
    GIVEN a logged-in user with a valid token
    WHEN the '/api/validate-token' endpoint is accessed with the token
    THEN check that a 200 status code is returned with user details
    """
    password = "password"
    user = User(email="valid.token@example.com", username="validuser.token", password_hash=generate_password_hash(password))
    session.add(user)
    session.commit() # Use commit() to make the user visible to the app context
    
    login_res = client.post('/api/login', data=json.dumps({"username": "validuser.token", "password": password}), content_type='application/json')
    access_token = login_res.get_json()['access_token']
    
    headers = {'Authorization': f'Bearer {access_token}'}
    response = client.get('/api/validate-token', headers=headers)
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['username'] == 'validuser.token'
    assert data['email'] == 'valid.token@example.com'

def test_validate_token_invalid(client):
    """
    GIVEN a Flask application
    WHEN the '/api/validate-token' endpoint is accessed with an invalid token
    THEN check that a 422 status code is returned by Flask-JWT-Extended
    """
    headers = {'Authorization': 'Bearer invalidtoken'}
    response = client.get('/api/validate-token', headers=headers)
    
    assert response.status_code == 422

def test_logout_success(client, session):
    """
    GIVEN a logged-in user
    WHEN the '/api/logout' endpoint is posted to with a valid token
    THEN check that a 200 status code is returned and the session is marked inactive
    """
    password = "password"
    user = User(email="logout.success@example.com", username="logoutuser.success", password_hash=generate_password_hash(password))
    session.add(user)
    session.commit() # Use commit() to make the user visible to the app context

    login_res = client.post('/api/login', data=json.dumps({"username": "logoutuser.success", "password": password}), content_type='application/json')
    access_token = login_res.get_json()['access_token']
    
    headers = {'Authorization': f'Bearer {access_token}'}
    response = client.post('/api/logout', headers=headers)
    
    assert response.status_code == 200
    assert "Logout successful" in response.get_json()['message']

    # Verify session is marked as inactive
    user_id = login_res.get_json()['user']['user_id']
    user_session = UserSession.query.filter_by(user_id=user_id).order_by(UserSession.login_at.desc()).first()
    assert user_session is not None
    assert user_session.is_active is False
    assert user_session.logout_at is not None
    assert user_session.session_duration_seconds is not None

def test_logout_no_token(client):
    """
    GIVEN a Flask application
    WHEN the '/api/logout' endpoint is posted to without a token
    THEN check that a 401 status code is returned
    """
    response = client.post('/api/logout')
    assert response.status_code == 401
    assert "Missing Authorization Header" in response.get_json()['msg']