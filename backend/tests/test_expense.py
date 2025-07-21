import json
import pytest
from model import db, User, UserProfile, Transaction
from werkzeug.security import generate_password_hash
from datetime import datetime
import uuid

# --- Fixtures for Users and Tokens ---

@pytest.fixture
def premium_user(session):
    """Creates and returns a unique premium user instance for each test."""
    unique_id = uuid.uuid4().hex[:8]
    password = "password123"
    user = User(email=f"premium_expense_{unique_id}@example.com", username=f"premium_expense_user_{unique_id}", password_hash=generate_password_hash(password))
    session.add(user)
    session.flush()
    profile = UserProfile(user_id=user.user_id, full_name="Premium Expense User", gender="female", birth_date=datetime.strptime("2000-01-01", "%Y-%m-%d").date(), is_premium_user=True)
    session.add(profile)
    session.flush()
    return user, password

@pytest.fixture
def premium_user_token(client, premium_user):
    """Logs in the premium user via the API and returns a valid token."""
    user, password = premium_user
    response = client.post('/api/login', data=json.dumps({'username': user.username, 'password': password}), content_type='application/json')
    assert response.status_code == 200, f"Login failed for premium user: {response.get_data(as_text=True)}"
    data = response.get_json()
    return data['access_token']

# --- Tests for Passcode Endpoints ---

def test_create_passcode_success(client, premium_user_token):
    """
    GIVEN a logged-in premium user
    WHEN the '/api/create_passcode' endpoint is posted to with a valid passcode
    THEN check that a 201 status code is returned and the passcode is set
    """
    headers = {'Authorization': f'Bearer {premium_user_token}'}
    response = client.post('/api/create_passcode',
                           headers=headers,
                           data=json.dumps({'passcode': 1234}),
                           content_type='application/json')
    assert response.status_code == 201
    assert response.get_json()['success'] is True

def test_get_passcode_status(client, premium_user_token):
    """
    GIVEN a logged-in premium user
    WHEN the '/api/get_passcode_status' endpoint is accessed before and after creating a passcode
    THEN check that the status is correctly reported as false and then true
    """
    headers = {'Authorization': f'Bearer {premium_user_token}'}
    
    # 1. Check status before creating a passcode
    response_before = client.get('/api/get_passcode_status', headers=headers)
    assert response_before.status_code == 202
    assert response_before.get_json()['exists'] is False

    # 2. Create a passcode
    client.post('/api/create_passcode', headers=headers, data=json.dumps({'passcode': 1234}), content_type='application/json')

    # 3. Check status after creating a passcode
    response_after = client.get('/api/get_passcode_status', headers=headers)
    assert response_after.status_code == 202
    assert response_after.get_json()['exists'] is True

def test_submit_passcode_correct_and_incorrect(client, premium_user_token):
    """
    GIVEN a premium user with a created passcode
    WHEN the '/api/submit_passcode' endpoint is used with correct and incorrect passcodes
    THEN check that the success status is reported correctly
    """
    headers = {'Authorization': f'Bearer {premium_user_token}'}
    # Create the passcode
    create_response = client.post('/api/create_passcode', headers=headers, data=json.dumps({'passcode': "5678"}), content_type='application/json')
    assert create_response.status_code == 201

    # Test with correct passcode
    response_correct = client.post('/api/submit_passcode',
                                   headers=headers,
                                   data=json.dumps({'passcode': '5678'}),
                                   content_type='application/json')
    assert response_correct.status_code == 200
    assert response_correct.get_json()['success'] is True 

    # Test with incorrect passcode
    response_incorrect = client.post('/api/submit_passcode',
                                     headers=headers,
                                     data=json.dumps({'passcode': 9999}),
                                     content_type='application/json')
    assert response_incorrect.status_code == 200
    assert response_incorrect.get_json()['success'] is False

# --- Tests for Transaction Endpoints ---

def test_add_expense_success(client, premium_user_token):
    """
    GIVEN a logged-in user
    WHEN the '/api/add_expense' endpoint is posted to with valid transaction data
    THEN check that a 201 status code is returned and the transaction is created
    """
    headers = {'Authorization': f'Bearer {premium_user_token}'}
    transaction_data = {
        "type": "expense",
        "date": "2025-07-21",
        "name": "Groceries",
        "category": "Food",
        "amount": 50.75
    }
    response = client.post('/api/add_expense',
                           headers=headers,
                           data=json.dumps(transaction_data),
                           content_type='application/json')
    
    assert response.status_code == 201
    data = response.get_json()
    assert data['name'] == "Groceries"
    assert data['category'] == "Food"

def test_add_expense_missing_details(client, premium_user_token):
    """
    GIVEN a logged-in user
    WHEN the '/api/add_expense' endpoint is posted to with missing details
    THEN check that a 500 status code is returned due to the broad exception handling
    """
    headers = {'Authorization': f'Bearer {premium_user_token}'}
    # Missing 'name'
    transaction_data = {
        "type": "expense",
        "date": "2025-07-21",
        "category": "Food",
        "amount": 50.75
    }
    response = client.post('/api/add_expense',
                           headers=headers,
                           data=json.dumps(transaction_data),
                           content_type='application/json')
    
    # The app's generic exception handler turns the 402 abort into a 500
    assert response.status_code == 500
    assert "An unexpected error occurred" in response.get_json()['message']

def test_get_all_expenses(client, session, premium_user_token):
    """
    GIVEN a user with existing transactions
    WHEN the '/api/get_all_expense' endpoint is accessed
    THEN check that a 200 status code is returned with a list of all transactions
    """
    # Corrected: Use the token from the fixture directly and clean the table for isolation.
    headers = {'Authorization': f'Bearer {premium_user_token}'}
    session.query(Transaction).delete()
    session.flush()
    
    # Add some transactions for the user associated with the token
    client.post('/api/add_expense', headers=headers, data=json.dumps({"type": "expense", "date": "2025-07-20", "name": "Movie Tickets", "category": "Entertainment", "amount": 25.00}), content_type='application/json')
    client.post('/api/add_expense', headers=headers, data=json.dumps({"type": "income", "date": "2025-07-19", "name": "Allowance", "category": "Income", "amount": 10.00}), content_type='application/json')

    # Now, get all transactions
    response = client.get('/api/get_all_expense', headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    # Assert the exact length now that the test is isolated
    assert len(data['expenses']) == 2
    assert any(d['name'] == 'Movie Tickets' for d in data['expenses'])
    assert any(d['name'] == 'Allowance' for d in data['expenses'])

def test_get_all_categories(client, session, premium_user_token):
    """
    GIVEN a user with transactions in multiple categories
    WHEN the '/api/get_all_categories' endpoint is accessed
    THEN check that a 202 status code is returned with a list of unique categories
    """
    headers = {'Authorization': f'Bearer {premium_user_token}'}
    # Corrected: Clean the table for an isolated test.
    session.query(Transaction).delete()
    session.flush()
    
    # Add transactions with different categories
    client.post('/api/add_expense', headers=headers, data=json.dumps({"type": "expense", "date": "2025-07-21", "name": "Bus Fare", "category": "Transport", "amount": 2.50}), content_type='application/json')
    client.post('/api/add_expense', headers=headers, data=json.dumps({"type": "expense", "date": "2025-07-21", "name": "Comics", "category": "Entertainment", "amount": 5.00}), content_type='application/json')
    client.post('/api/add_expense', headers=headers, data=json.dumps({"type": "expense", "date": "2025-07-21", "name": "Train Fare", "category": "Transport", "amount": 3.00}), content_type='application/json')

    # Get all categories
    response = client.get('/api/get_all_categories', headers=headers)
    assert response.status_code == 202
    data = response.get_json()
    categories = {item['category'] for item in data}
    assert "Transport" in categories
    assert "Entertainment" in categories
    # Assert the exact length now that the test is isolated
    assert len(categories) == 2
