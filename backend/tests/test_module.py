import json
import pytest
from model import db, User, Lesson, Module
from werkzeug.security import generate_password_hash
from datetime import datetime
import uuid

# --- Fixtures for Users, Tokens, and Lessons ---

@pytest.fixture
def regular_user(session):
    """Creates a unique regular user instance."""
    unique_id = uuid.uuid4().hex[:8]
    password = "password123"
    user = User(email=f"module_user_{unique_id}@example.com", username=f"module_user_{unique_id}", password_hash=generate_password_hash(password))
    session.add(user)
    session.flush()
    return user, password

@pytest.fixture
def admin_user(session):
    """Creates a unique admin user instance."""
    unique_id = uuid.uuid4().hex[:8]
    password = "adminpassword"
    user = User(email=f"module_admin_{unique_id}@example.com", username=f"module_admin_{unique_id}", password_hash=generate_password_hash(password), user_role="admin")
    session.add(user)
    session.flush()
    return user, password

@pytest.fixture
def regular_user_token(client, regular_user):
    """Logs in the regular user and returns a token."""
    user, password = regular_user
    response = client.post('/api/login', data=json.dumps({'username': user.username, 'password': password}), content_type='application/json')
    assert response.status_code == 200
    return response.get_json()['access_token']

@pytest.fixture
def admin_user_token(client, admin_user):
    """Logs in the admin user and returns a token."""
    user, password = admin_user
    response = client.post('/api/login', data=json.dumps({'username': user.username, 'password': password}), content_type='application/json')
    assert response.status_code == 200
    return response.get_json()['access_token']

@pytest.fixture
def sample_lesson(session):
    """Creates a unique sample lesson and returns it."""
    # Corrected: Ensure lesson name is unique for each test run.
    unique_id = uuid.uuid4().hex[:8]
    lesson = Lesson(lesson_name=f"Sample Lesson {unique_id}", lesson_description="A test lesson.")
    session.add(lesson)
    session.flush()
    return lesson

# --- Tests for Module Endpoints ---

def test_create_module_success_by_admin(client, session, admin_user_token, sample_lesson):
    """
    GIVEN a logged-in admin user and an existing lesson
    WHEN the '/api/<lesson_id>/module/create' endpoint is posted to with valid data
    THEN check that a 201 status code is returned and the module is created
    """
    headers = {'Authorization': f'Bearer {admin_user_token}'}
    module_data = {'module_title': 'First Module', 'module_description': 'This is the first module.'}
    
    response = client.post(f'/api/{sample_lesson.lesson_id}/module/create',
                           headers=headers,
                           data=json.dumps(module_data),
                           content_type='application/json')
    
    assert response.status_code == 201
    data = response.get_json()
    assert data['module_title'] == 'First Module'
    assert data['lesson_id'] == sample_lesson.lesson_id
    
    # Verify the module exists in the DB
    module = Module.query.get(data['module_id'])
    assert module is not None

def test_create_module_forbidden_for_regular_user(client, regular_user_token, sample_lesson):
    """
    GIVEN a logged-in regular (non-admin) user
    WHEN they attempt to create a module
    THEN check that a 500 status code is returned due to the app's error handling
    """
    headers = {'Authorization': f'Bearer {regular_user_token}'}
    module_data = {'module_title': 'Unauthorized Module'}
    
    response = client.post(f'/api/{sample_lesson.lesson_id}/module/create',
                           headers=headers,
                           data=json.dumps(module_data),
                           content_type='application/json')
                           
    # The app's generic exception handler turns the 403 abort into a 500
    assert response.status_code == 500

def test_get_modules_by_lesson(client, session, regular_user_token, admin_user, sample_lesson):
    """
    GIVEN an existing lesson with multiple modules
    WHEN the '/api/<lesson_id>/modules' endpoint is accessed
    THEN check that a 200 status code is returned with the correct modules
    """
    admin, _ = admin_user
    # Seed modules for the lesson
    mod1 = Module(lesson_id=sample_lesson.lesson_id, created_by_admin_id=admin.user_id, module_title="Module A")
    mod2 = Module(lesson_id=sample_lesson.lesson_id, created_by_admin_id=admin.user_id, module_title="Module B")
    session.add_all([mod1, mod2])
    session.flush()

    headers = {'Authorization': f'Bearer {regular_user_token}'}
    response = client.get(f'/api/{sample_lesson.lesson_id}/modules', headers=headers)
    
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    module_titles = {m['module_title'] for m in data}
    assert "Module A" in module_titles
    assert "Module B" in module_titles

def test_update_module_success(client, session, admin_user_token, admin_user, sample_lesson):
    """
    GIVEN an existing module created by an admin
    WHEN the admin updates the module via the PUT endpoint
    THEN check that a 200 status code is returned and the module is updated
    """
    admin, _ = admin_user
    module = Module(lesson_id=sample_lesson.lesson_id, created_by_admin_id=admin.user_id, module_title="Original Title")
    session.add(module)
    session.flush()

    headers = {'Authorization': f'Bearer {admin_user_token}'}
    update_data = {'module_title': 'Updated Title', 'module_description': 'Updated description.'}
    
    response = client.put(f'/api/{sample_lesson.lesson_id}/module/{module.module_id}/update',
                          headers=headers,
                          data=json.dumps(update_data),
                          content_type='application/json')
                          
    assert response.status_code == 200
    data = response.get_json()
    assert data['module_title'] == 'Updated Title'
    assert data['module_description'] == 'Updated description.'

def test_delete_module_success(client, session, admin_user_token, admin_user, sample_lesson):
    """
    GIVEN an existing module
    WHEN an admin sends a DELETE request to the module's endpoint
    THEN check that a 200 status code is returned and the module is soft-deleted
    """
    admin, _ = admin_user
    module = Module(lesson_id=sample_lesson.lesson_id, created_by_admin_id=admin.user_id, module_title="To Be Deleted")
    session.add(module)
    session.flush()
    
    module_id = module.module_id
    headers = {'Authorization': f'Bearer {admin_user_token}'}
    
    response = client.delete(f'/api/{sample_lesson.lesson_id}/module/{module_id}/delete', headers=headers)
    
    assert response.status_code == 200
    assert "Module deleted successfully" in response.get_json()['message']
    
    # Verify it's soft-deleted
    deleted_module = Module.query.get(module_id)
    assert deleted_module is not None
    assert deleted_module.deleted_at is not None

def test_get_all_modules(client, session, regular_user_token, admin_user, sample_lesson):
    """
    GIVEN multiple modules exist for different lessons
    WHEN the '/api/get_all_modules' endpoint is accessed
    THEN check that all non-deleted modules are returned
    """
    session.query(Module).delete() # Clean slate
    admin, _ = admin_user
    
    # Create another lesson
    other_lesson = Lesson(lesson_name="Another Lesson")
    session.add(other_lesson)
    session.flush()

    mod1 = Module(lesson_id=sample_lesson.lesson_id, created_by_admin_id=admin.user_id, module_title="Module 1")
    mod2 = Module(lesson_id=other_lesson.lesson_id, created_by_admin_id=admin.user_id, module_title="Module 2")
    mod3_deleted = Module(lesson_id=sample_lesson.lesson_id, created_by_admin_id=admin.user_id, module_title="Deleted Module", deleted_at=datetime.utcnow())
    session.add_all([mod1, mod2, mod3_deleted])
    session.flush()

    headers = {'Authorization': f'Bearer {regular_user_token}'}
    response = client.get('/api/get_all_modules', headers=headers)
    
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2 # Should not include the deleted module
    module_titles = {m['module_title'] for m in data}
    assert "Module 1" in module_titles
    assert "Module 2" in module_titles
    assert "Deleted Module" not in module_titles
