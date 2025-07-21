import json
import pytest
from unittest.mock import patch, MagicMock
from model import db, User, Lesson, Module, Topic, UserModuleProgress
from werkzeug.security import generate_password_hash
from datetime import datetime
import uuid
import io

# --- Fixtures for Users, Tokens, and Learning Structure ---

@pytest.fixture
def regular_user(session):
    """Creates a unique regular user instance."""
    unique_id = uuid.uuid4().hex[:8]
    password = "password123"
    user = User(email=f"topic_user_{unique_id}@example.com", username=f"topic_user_{unique_id}", password_hash=generate_password_hash(password))
    session.add(user)
    session.flush()
    return user, password

@pytest.fixture
def admin_user(session):
    """Creates a unique admin user instance."""
    unique_id = uuid.uuid4().hex[:8]
    password = "adminpassword"
    user = User(email=f"topic_admin_{unique_id}@example.com", username=f"topic_admin_{unique_id}", password_hash=generate_password_hash(password), user_role="admin")
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
def sample_lesson_module(session, admin_user):
    """Creates a sample lesson and module, returning them."""
    admin, _ = admin_user
    lesson = Lesson(lesson_name=f"Lesson for Topics {uuid.uuid4().hex[:4]}")
    session.add(lesson)
    session.flush()
    module = Module(lesson_id=lesson.lesson_id, module_title=f"Module for Topics {uuid.uuid4().hex[:4]}", created_by_admin_id=admin.user_id)
    session.add(module)
    session.flush()
    return lesson, module

# --- Tests for Topic CRUD and Retrieval ---

def test_create_topic_success(client, admin_user_token, sample_lesson_module):
    """
    GIVEN an admin user and an existing module
    WHEN creating a new topic
    THEN check for a 201 status and correct data
    """
    lesson, module = sample_lesson_module
    headers = {'Authorization': f'Bearer {admin_user_token}'}
    response = client.post(f'/api/{lesson.lesson_id}/module/{module.module_id}/topic/create',
                           headers=headers,
                           data=json.dumps({'topic_title': 'New Topic'}),
                           content_type='application/json')
    assert response.status_code == 201
    data = response.get_json()
    assert data['topic_title'] == 'New Topic'
    assert data['module_id'] == module.module_id

def test_get_topics_by_module(client, session, regular_user_token, admin_user, sample_lesson_module):
    """
    GIVEN a module with several topics
    WHEN retrieving topics for that module
    THEN check for a 200 status and the correct list of topics
    """
    lesson, module = sample_lesson_module
    admin, _ = admin_user
    # Seed topics
    session.add(Topic(module_id=module.module_id, created_by_admin_id=admin.user_id, topic_title='Topic 1'))
    session.add(Topic(module_id=module.module_id, created_by_admin_id=admin.user_id, topic_title='Topic 2'))
    session.flush()

    headers = {'Authorization': f'Bearer {regular_user_token}'}
    response = client.get(f'/api/{lesson.lesson_id}/module/{module.module_id}/topics', headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    assert {'Topic 1', 'Topic 2'} == {t['topic_title'] for t in data}

def test_update_topic_success(client, session, admin_user_token, admin_user, sample_lesson_module):
    """
    GIVEN an existing topic
    WHEN an admin updates its title
    THEN check for a 200 status and that the title is updated
    """
    lesson, module = sample_lesson_module
    admin, _ = admin_user
    topic = Topic(module_id=module.module_id, created_by_admin_id=admin.user_id, topic_title='Old Title')
    session.add(topic)
    session.flush()

    headers = {'Authorization': f'Bearer {admin_user_token}'}
    response = client.put(f'/api/{lesson.lesson_id}/module/{module.module_id}/topic/{topic.topic_id}/update',
                          headers=headers,
                          data=json.dumps({'topic_title': 'New Title'}),
                          content_type='application/json')
    assert response.status_code == 200
    assert response.get_json()['topic_title'] == 'New Title'

def test_delete_topic_success(client, session, admin_user_token, admin_user, sample_lesson_module):
    """
    GIVEN an existing topic
    WHEN an admin deletes it
    THEN check that it is soft-deleted and no longer appears in lists
    """
    lesson, module = sample_lesson_module
    admin, _ = admin_user
    topic = Topic(module_id=module.module_id, created_by_admin_id=admin.user_id, topic_title='To Delete')
    session.add(topic)
    session.flush()

    headers = {'Authorization': f'Bearer {admin_user_token}'}
    delete_response = client.delete(f'/api/{lesson.lesson_id}/module/{module.module_id}/topic/{topic.topic_id}/delete', headers=headers)
    assert delete_response.status_code == 200

    # Verify it's gone from the list
    get_response = client.get(f'/api/{lesson.lesson_id}/module/{module.module_id}/topics', headers=headers)
    assert not any(t['topic_id'] == topic.topic_id for t in get_response.get_json())

# --- Tests for Content Management ---

@patch('routes.topic.magic.Magic')
def test_upload_and_download_content_success(mock_magic, client, session, admin_user_token, regular_user_token, admin_user, sample_lesson_module):
    """
    GIVEN a topic without content
    WHEN an admin uploads a PDF and a user downloads it
    THEN check for successful upload and correct file download
    """
    mock_magic.return_value.from_buffer.return_value = 'application/pdf'
    lesson, module = sample_lesson_module
    admin, _ = admin_user
    topic = Topic(module_id=module.module_id, created_by_admin_id=admin.user_id, topic_title='PDF Topic')
    session.add(topic)
    session.flush()

    # Admin uploads content
    admin_headers = {'Authorization': f'Bearer {admin_user_token}'}
    pdf_content = b'%PDF-1.5 fake pdf content'
    data = {'content_file': (io.BytesIO(pdf_content), 'test.pdf')}
    upload_response = client.post(f'/api/{lesson.lesson_id}/module/{module.module_id}/topic/{topic.topic_id}/upload_content',
                                  headers=admin_headers, data=data, content_type='multipart/form-data')
    assert upload_response.status_code == 200

    # User downloads content
    user_headers = {'Authorization': f'Bearer {regular_user_token}'}
    download_response = client.get(f'/api/{lesson.lesson_id}/module/{module.module_id}/topic/{topic.topic_id}/download_content', headers=user_headers)
    assert download_response.status_code == 200
    assert download_response.data == pdf_content
    assert download_response.mimetype == 'application/pdf'

# --- Tests for User Progress ---

def test_start_and_get_progress(client, regular_user_token, sample_lesson_module):
    """
    GIVEN a topic a user has not started
    WHEN the user starts the topic and then checks progress
    THEN check that progress is created and reported as 0%
    """
    lesson, module = sample_lesson_module
    # We need a topic to exist first
    topic = Topic(module_id=module.module_id, created_by_admin_id=1, topic_title="Progress Topic")
    db.session.add(topic)
    db.session.flush()

    headers = {'Authorization': f'Bearer {regular_user_token}'}

    # Start progress
    start_response = client.post(f'/api/progress/lesson/{lesson.lesson_id}/module/{module.module_id}/topic/{topic.topic_id}/start', headers=headers)
    assert start_response.status_code == 200

    # Get progress
    get_response = client.get(f'/api/progress/lesson/{lesson.lesson_id}/module/{module.module_id}/topic/{topic.topic_id}', headers=headers)
    assert get_response.status_code == 200
    data = get_response.get_json()
    assert data['progress_percentage'] == 0
    assert data['topic_id'] == topic.topic_id

def test_complete_progress(client, regular_user_token, sample_lesson_module):
    """
    GIVEN a topic a user has started
    WHEN the user completes the topic
    THEN check that progress is updated to 100%
    """
    lesson, module = sample_lesson_module
    topic = Topic(module_id=module.module_id, created_by_admin_id=1, topic_title="Completable Topic")
    db.session.add(topic)
    db.session.flush()

    headers = {'Authorization': f'Bearer {regular_user_token}'}

    # Start progress first
    client.post(f'/api/progress/lesson/{lesson.lesson_id}/module/{module.module_id}/topic/{topic.topic_id}/start', headers=headers)

    # Complete progress
    complete_response = client.post(f'/api/progress/lesson/{lesson.lesson_id}/module/{module.module_id}/topic/{topic.topic_id}/complete', headers=headers)
    assert complete_response.status_code == 200
    assert complete_response.get_json()['progress_percentage'] == 100
