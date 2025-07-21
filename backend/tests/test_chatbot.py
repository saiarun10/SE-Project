import json
import pytest
from unittest.mock import patch
from model import db, User, UserProfile, UserSession, ChatbotMessage
from werkzeug.security import generate_password_hash
from datetime import datetime
import uuid

@pytest.fixture
def premium_user(session):
    """Creates and returns a unique premium user instance for each test."""
    unique_id = uuid.uuid4().hex[:8]
    password = "password123"
    user = User(email=f"premium_{unique_id}@example.com", username=f"premiumuser_{unique_id}", password_hash=generate_password_hash(password))
    session.add(user)
    session.flush()
    profile = UserProfile(user_id=user.user_id, full_name="Premium User", gender="female", birth_date=datetime.strptime("2000-01-01", "%Y-%m-%d").date(), is_premium_user=True)
    session.add(profile)
    session.flush()
    return user, password

@pytest.fixture
def non_premium_user(session):
    """Creates and returns a unique non-premium user instance for each test."""
    unique_id = uuid.uuid4().hex[:8]
    password = "password123"
    user = User(email=f"nonpremium_{unique_id}@example.com", username=f"nonpremiumuser_{unique_id}", password_hash=generate_password_hash(password))
    session.add(user)
    session.flush()
    profile = UserProfile(user_id=user.user_id, full_name="Non-Premium User", gender="male", birth_date=datetime.strptime("2005-01-01", "%Y-%m-%d").date(), is_premium_user=False)
    session.add(profile)
    session.flush()
    return user, password

@pytest.fixture
def admin_user(session):
    """Creates and returns a unique admin user instance for each test."""
    unique_id = uuid.uuid4().hex[:8]
    password = "adminpassword"
    user = User(email=f"admin_{unique_id}@example.com", username=f"adminuser_{unique_id}", password_hash=generate_password_hash(password), user_role="admin")
    session.add(user)
    session.flush()
    return user, password

@pytest.fixture
def premium_user_token(client, premium_user):
    """Logs in the premium user via the API and returns token and user info."""
    user, password = premium_user
    response = client.post('/api/login', data=json.dumps({'username': user.username, 'password': password}), content_type='application/json')
    assert response.status_code == 200, f"Login failed for premium user: {response.get_data(as_text=True)}"
    data = response.get_json()
    user_session = UserSession.query.filter_by(user_id=user.user_id, is_active=True).one()
    return data['access_token'], user.user_id, user_session.session_id

@pytest.fixture
def non_premium_user_token(client, non_premium_user):
    """Logs in the non-premium user via the API and returns token and user info."""
    user, password = non_premium_user
    response = client.post('/api/login', data=json.dumps({'username': user.username, 'password': password}), content_type='application/json')
    assert response.status_code == 200, f"Login failed for non-premium user: {response.get_data(as_text=True)}"
    data = response.get_json()
    user_session = UserSession.query.filter_by(user_id=user.user_id, is_active=True).one()
    return data['access_token'], user.user_id, user_session.session_id

@pytest.fixture
def admin_user_token(client, admin_user):
    """Logs in the admin user via the API and returns a token."""
    user, password = admin_user
    response = client.post('/api/login', data=json.dumps({'username': user.username, 'password': password}), content_type='application/json')
    assert response.status_code == 200, f"Login failed for admin user: {response.get_data(as_text=True)}"
    data = response.get_json()
    return data['access_token']

# --- Tests for Chatbot Endpoints ---

@patch('routes.chatbot.groq_service')
def test_send_message_success(mock_groq_service, client, premium_user_token):
    """
    GIVEN a logged-in premium user and a mocked Groq service
    WHEN the '/api/send_message' endpoint is posted to with a valid message
    THEN check that a 200 status code is returned and the bot's reply is correct
    """
    mock_groq_service.get_chat_response.return_value = "Hello! I am FinBot."
    
    access_token, _, _ = premium_user_token
    headers = {'Authorization': f'Bearer {access_token}'}
    
    response = client.post('/api/send_message',
                           headers=headers,
                           data=json.dumps({'message': 'Hi there!'}),
                           content_type='application/json')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['reply']['sender'] == 'bot'
    assert data['reply']['text'] == "Hello! I am FinBot."
    mock_groq_service.get_chat_response.assert_called_once()

@patch('routes.chatbot.groq_service')
def test_send_message_non_premium_limit(mock_groq_service, client, session, non_premium_user_token):
    """
    GIVEN a non-premium user who has already sent 10 messages
    WHEN they attempt to send an 11th message
    THEN check that a 403 Forbidden status is returned
    """
    access_token, user_id, session_id = non_premium_user_token

    for i in range(10):
        msg = ChatbotMessage(user_id=user_id, session_id=session_id, message_content=f"Message {i}", message_type='user')
        session.add(msg)
    session.flush()

    headers = {'Authorization': f'Bearer {access_token}'}
    response = client.post('/api/send_message',
                           headers=headers,
                           data=json.dumps({'message': 'My eleventh message'}),
                           content_type='application/json')
    
    assert response.status_code == 403
    assert "reached your message limit" in response.get_json()['message']

def test_send_message_empty(client, premium_user_token):
    """
    GIVEN a logged-in user
    WHEN they send an empty message
    THEN check that a 400 Bad Request status is returned
    """
    access_token, _, _ = premium_user_token
    headers = {'Authorization': f'Bearer {access_token}'}
    
    response = client.post('/api/send_message',
                           headers=headers,
                           data=json.dumps({'message': ''}),
                           content_type='application/json')
    
    assert response.status_code == 400
    assert "cannot be empty" in response.get_json()['message']

@patch('routes.chatbot.groq_service', None)
def test_send_message_service_unavailable(client, premium_user_token):
    """
    GIVEN the Groq service is unavailable (mocked as None)
    WHEN a user tries to send a message
    THEN check that a 503 Service Unavailable status is returned
    """
    access_token, _, _ = premium_user_token
    headers = {'Authorization': f'Bearer {access_token}'}
    
    response = client.post('/api/send_message',
                           headers=headers,
                           data=json.dumps({'message': 'Does this work?'}),
                           content_type='application/json')
    
    assert response.status_code == 503
    assert "service is currently unavailable" in response.get_json()['message']

def test_get_chat_history_success(client, session, premium_user_token):
    """
    GIVEN a user with an active session and chat history
    WHEN they request their chat history
    THEN check that a 200 status is returned with the correct messages
    """
    access_token, user_id, session_id = premium_user_token

    msg1 = ChatbotMessage(user_id=user_id, session_id=session_id, message_content="Hello", message_type='user', sent_at=datetime.now())
    msg2 = ChatbotMessage(user_id=user_id, session_id=session_id, message_content="Hi back!", message_type='bot', sent_at=datetime.now())
    session.add_all([msg1, msg2])
    session.flush()

    headers = {'Authorization': f'Bearer {access_token}'}
    response = client.get('/api/chat_history', headers=headers)

    assert response.status_code == 200
    data = response.get_json()
    assert len(data['history']) == 2
    assert data['history'][0]['sender'] == 'user'
    assert data['history'][0]['text'] == 'Hello'
    assert data['history'][1]['sender'] == 'bot'
    assert data['history'][1]['text'] == 'Hi back!'

def test_get_chatbot_stats_admin_success(client, session, admin_user_token, premium_user_token, non_premium_user_token):
    """
    GIVEN an admin user and some chat data
    WHEN the '/api/chatbot_stats' endpoint is accessed
    THEN check that a 200 status is returned with correct, calculated statistics
    """
    # Corrected: Clean the table to ensure an isolated test environment.
    session.query(ChatbotMessage).delete()
    session.flush()

    _, premium_user_id, prem_session_id = premium_user_token
    _, non_prem_user_id, non_prem_session_id = non_premium_user_token

    session.add(ChatbotMessage(user_id=premium_user_id, session_id=prem_session_id, message_content="P1", message_type='user'))
    session.add(ChatbotMessage(user_id=premium_user_id, session_id=prem_session_id, message_content="B1", message_type='bot'))
    session.add(ChatbotMessage(user_id=non_prem_user_id, session_id=non_prem_session_id, message_content="NP1", message_type='user'))
    session.add(ChatbotMessage(user_id=non_prem_user_id, session_id=non_prem_session_id, message_content="B2", message_type='bot'))
    session.add(ChatbotMessage(user_id=non_prem_user_id, session_id=non_prem_session_id, message_content="NP2", message_type='user'))
    session.flush()

    headers = {'Authorization': f'Bearer {admin_user_token}'}
    response = client.get('/api/chatbot_stats', headers=headers)

    assert response.status_code == 200
    stats = response.get_json()
    assert stats['total_messages'] == 5
    assert stats['total_user_messages'] == 3
    assert stats['total_bot_responses'] == 2
    assert stats['unique_users_chatted'] == 2
    assert stats['premium_users_chatted'] == 1
    assert stats['non_premium_users_chatted'] == 1
    assert stats['active_users_today'] == 0
    assert stats['avg_messages_per_user'] == 1.5
    assert stats['avg_messages_per_session'] == 2.5

def test_get_chatbot_stats_non_admin_forbidden(client, premium_user_token):
    """
    GIVEN a non-admin user
    WHEN they attempt to access chatbot stats
    THEN check that a 403 Forbidden status is returned
    """
    access_token, _, _ = premium_user_token
    headers = {'Authorization': f'Bearer {access_token}'}
    
    response = client.get('/api/chatbot_stats', headers=headers)
    
    assert response.status_code == 403
    assert "Admin access required" in response.get_json()['message']
