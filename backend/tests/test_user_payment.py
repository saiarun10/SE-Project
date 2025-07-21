import json
import pytest
from unittest.mock import patch, MagicMock
from model import db, User, UserProfile
from werkzeug.security import generate_password_hash
from datetime import datetime
import uuid

# --- Fixtures for Users and Tokens ---

@pytest.fixture
def non_premium_user(session):
    """Creates a unique non-premium user with a profile."""
    unique_id = uuid.uuid4().hex[:8]
    password = "password123"
    user = User(email=f"payment_user_{unique_id}@example.com", username=f"payment_user_{unique_id}", password_hash=generate_password_hash(password))
    session.add(user)
    session.flush()
    profile = UserProfile(user_id=user.user_id, full_name="Payment User", gender="male", birth_date=datetime(2010, 1, 1).date(), is_premium_user=False)
    session.add(profile)
    session.flush()
    return user, password

@pytest.fixture
def premium_user(session):
    """Creates a unique premium user with a profile."""
    unique_id = uuid.uuid4().hex[:8]
    password = "password123"
    user = User(email=f"payment_prem_{unique_id}@example.com", username=f"payment_prem_{unique_id}", password_hash=generate_password_hash(password))
    session.add(user)
    session.flush()
    profile = UserProfile(user_id=user.user_id, full_name="Already Premium", gender="female", birth_date=datetime(2010, 1, 1).date(), is_premium_user=True)
    session.add(profile)
    session.flush()
    return user, password

@pytest.fixture
def non_premium_user_token(client, non_premium_user):
    """Logs in the non-premium user and returns a token and user object."""
    user, password = non_premium_user
    response = client.post('/api/login', data=json.dumps({'username': user.username, 'password': password}), content_type='application/json')
    assert response.status_code == 200
    return response.get_json()['access_token'], user

@pytest.fixture
def premium_user_token(client, premium_user):
    """Logs in the premium user and returns a token."""
    user, password = premium_user
    response = client.post('/api/login', data=json.dumps({'username': user.username, 'password': password}), content_type='application/json')
    assert response.status_code == 200
    return response.get_json()['access_token']

# --- Tests for Payment Endpoints ---

@patch('routes.user_payment.stripe.checkout.Session.create')
def test_create_checkout_session_success(mock_stripe_create, client, non_premium_user_token):
    """
    GIVEN a logged-in non-premium user
    WHEN the '/api/payment-create-checkout-session' endpoint is called
    THEN check that a Stripe session is created and the URL is returned
    """
    mock_stripe_create.return_value = MagicMock(url='https://stripe.com/checkout/test', id='cs_test_123')
    
    token, _ = non_premium_user_token
    headers = {'Authorization': f'Bearer {token}'}
    
    response = client.post('/api/payment-create-checkout-session', headers=headers)
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['url'] == 'https://stripe.com/checkout/test'
    assert data['session_id'] == 'cs_test_123'
    mock_stripe_create.assert_called_once()

def test_create_checkout_session_already_premium(client, premium_user_token):
    """
    GIVEN a user who is already a premium member
    WHEN they attempt to create a checkout session
    THEN check that a 400 Bad Request status is returned
    """
    headers = {'Authorization': f'Bearer {premium_user_token}'}
    response = client.post('/api/payment-create-checkout-session', headers=headers)
    
    assert response.status_code == 400
    assert "already a premium member" in response.get_json()['message']

@patch('routes.user_payment.stripe.checkout.Session.retrieve')
def test_verify_payment_success(mock_stripe_retrieve, client, session, non_premium_user_token):
    """
    GIVEN a non-premium user with a 'paid' Stripe session
    WHEN the '/api/verify-payment' endpoint is called with the session ID
    THEN check that the user's premium status is updated to True
    """
    token, user = non_premium_user_token
    session_id = 'cs_test_paid'
    
    # Mock the Stripe API response
    mock_stripe_retrieve.return_value = MagicMock(
        payment_status='paid',
        client_reference_id=str(user.user_id)
    )
    
    headers = {'Authorization': f'Bearer {token}'}
    response = client.post('/api/verify-payment', 
                           headers=headers, 
                           data=json.dumps({'session_id': session_id}),
                           content_type='application/json')

    assert response.status_code == 200
    assert response.get_json()['message'] == 'Payment successful and account upgraded!'
    assert response.get_json()['is_premium'] is True
    
    # Verify the database was updated
    updated_profile = UserProfile.query.filter_by(user_id=user.user_id).one()
    assert updated_profile.is_premium_user is True

@patch('routes.user_payment.stripe.checkout.Session.retrieve')
def test_verify_payment_unpaid(mock_stripe_retrieve, client, non_premium_user_token):
    """
    GIVEN a non-premium user with an 'unpaid' Stripe session
    WHEN the '/api/verify-payment' endpoint is called
    THEN check that a 400 status is returned and the user remains non-premium
    """
    token, user = non_premium_user_token
    session_id = 'cs_test_unpaid'
    
    mock_stripe_retrieve.return_value = MagicMock(
        payment_status='unpaid',
        client_reference_id=str(user.user_id)
    )
    
    headers = {'Authorization': f'Bearer {token}'}
    response = client.post('/api/verify-payment', 
                           headers=headers, 
                           data=json.dumps({'session_id': session_id}),
                           content_type='application/json')
                           
    assert response.status_code == 400
    assert "Payment not completed" in response.get_json()['message']

@patch('routes.user_payment.stripe.checkout.Session.retrieve')
def test_verify_payment_wrong_user(mock_stripe_retrieve, client, non_premium_user_token):
    """
    GIVEN a user trying to verify a payment session that belongs to someone else
    WHEN the '/api/verify-payment' endpoint is called
    THEN check that a 403 Forbidden status is returned
    """
    token, _ = non_premium_user_token
    session_id = 'cs_test_wrong_user'
    
    mock_stripe_retrieve.return_value = MagicMock(
        payment_status='paid',
        client_reference_id='999' # A different user ID
    )
    
    headers = {'Authorization': f'Bearer {token}'}
    response = client.post('/api/verify-payment', 
                           headers=headers, 
                           data=json.dumps({'session_id': session_id}),
                           content_type='application/json')
                           
    assert response.status_code == 403
    assert "Session does not belong to user" in response.get_json()['message']

def test_get_user_premium_status(client, non_premium_user_token, premium_user_token):
    """
    GIVEN both a premium and a non-premium user
    WHEN their status is checked via the '/api/user-premium-status' endpoint
    THEN check that the correct status is returned for each
    """
    # Test non-premium user
    non_prem_token, _ = non_premium_user_token
    headers_non_prem = {'Authorization': f'Bearer {non_prem_token}'}
    response_non_prem = client.get('/api/user-premium-status', headers=headers_non_prem)
    assert response_non_prem.status_code == 200
    assert response_non_prem.get_json()['is_premium'] is False

    # Test premium user
    headers_prem = {'Authorization': f'Bearer {premium_user_token}'}
    response_prem = client.get('/api/user-premium-status', headers=headers_prem)
    assert response_prem.status_code == 200
    assert response_prem.get_json()['is_premium'] is True
