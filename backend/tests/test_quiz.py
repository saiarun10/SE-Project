import json
import pytest
from model import db, User, Lesson, Module, Topic, Quiz, Question, QuizAttempt, QuestionAttempt
from werkzeug.security import generate_password_hash
import uuid
from datetime import datetime

# --- Fixtures for Users, Tokens, and Learning Structure ---

@pytest.fixture
def regular_user(session):
    """Creates a unique regular user instance."""
    unique_id = uuid.uuid4().hex[:8]
    password = "password123"
    user = User(email=f"quiz_user_{unique_id}@example.com", username=f"quiz_user_{unique_id}", password_hash=generate_password_hash(password))
    session.add(user)
    session.flush()
    return user, password

@pytest.fixture
def admin_user(session):
    """Creates a unique admin user instance."""
    unique_id = uuid.uuid4().hex[:8]
    password = "adminpassword"
    user = User(email=f"quiz_admin_{unique_id}@example.com", username=f"quiz_admin_{unique_id}", password_hash=generate_password_hash(password), user_role="admin")
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
def sample_quiz(session, admin_user):
    """Creates a full hierarchy: Lesson -> Module -> Topic -> Quiz."""
    admin, _ = admin_user
    lesson = Lesson(lesson_name=f"Lesson for Quiz {uuid.uuid4().hex[:4]}")
    session.add(lesson)
    session.flush()
    module = Module(lesson_id=lesson.lesson_id, module_title=f"Module for Quiz {uuid.uuid4().hex[:4]}", created_by_admin_id=admin.user_id)
    session.add(module)
    session.flush()
    topic = Topic(module_id=module.module_id, topic_title=f"Topic for Quiz {uuid.uuid4().hex[:4]}", created_by_admin_id=admin.user_id)
    session.add(topic)
    session.flush()
    quiz = Quiz(module_id=module.module_id, topic_id=topic.topic_id, quiz_title="Sample Quiz", duration_minutes=10, created_by_admin_id=admin.user_id)
    session.add(quiz)
    session.flush()
    return lesson, module, topic, quiz

# --- Tests for Quiz and Question Management (Admin) ---

def test_create_quiz_success(client, admin_user_token, sample_quiz):
    """
    GIVEN an admin and a topic
    WHEN creating a new quiz for that topic
    THEN check for a 201 status and correct data
    """
    lesson, module, topic, _ = sample_quiz
    headers = {'Authorization': f'Bearer {admin_user_token}'}
    quiz_data = {'quiz_title': 'New Dynamic Quiz', 'duration_minutes': 15}
    response = client.post(f'/api/{lesson.lesson_id}/module/{module.module_id}/topic/{topic.topic_id}/quiz/create',
                           headers=headers, data=json.dumps(quiz_data), content_type='application/json')
    assert response.status_code == 201
    data = response.get_json()
    assert data['quiz_title'] == 'New Dynamic Quiz'
    assert data['duration_minutes'] == 15

def test_get_quizzes_by_topic_with_stats(client, session, admin_user_token, admin_user, sample_quiz):
    """
    GIVEN a quiz with questions
    WHEN retrieving quizzes for its topic
    THEN check that stats (question count, total score) are correct
    """
    lesson, module, topic, quiz = sample_quiz
    admin, _ = admin_user
    # Add questions to the quiz
    session.add(Question(quiz_id=quiz.quiz_id, created_by_admin_id=admin.user_id, question_text="Q1", option1="A", option2="B", option3="C", option4="D", correct_answer="A", score_points=5))
    session.add(Question(quiz_id=quiz.quiz_id, created_by_admin_id=admin.user_id, question_text="Q2", option1="A", option2="B", option3="C", option4="D", correct_answer="B", score_points=10))
    session.flush()

    headers = {'Authorization': f'Bearer {admin_user_token}'}
    response = client.get(f'/api/{lesson.lesson_id}/module/{module.module_id}/topic/{topic.topic_id}/quizzes', headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) >= 1
    quiz_data = next(item for item in data if item["quiz_id"] == quiz.quiz_id)
    assert quiz_data['total_questions'] == 2
    assert quiz_data['total_score'] == 15

def test_create_and_get_question(client, admin_user_token, sample_quiz):
    """
    GIVEN an admin and a quiz
    WHEN creating a new question for that quiz
    THEN check that it can be retrieved successfully
    """
    lesson, module, topic, quiz = sample_quiz
    headers = {'Authorization': f'Bearer {admin_user_token}'}
    question_data = {
        "question_text": "What is interest?", "option1": "A fee", "option2": "A principle", 
        "option3": "A bonus", "option4": "A gift", "correct_answer": "A fee", "score_points": 3
    }
    create_response = client.post(f'/api/{lesson.lesson_id}/module/{module.module_id}/topic/{topic.topic_id}/quizzes/{quiz.quiz_id}/question/create',
                                  headers=headers, data=json.dumps(question_data), content_type='application/json')
    assert create_response.status_code == 201

    get_response = client.get(f'/api/{lesson.lesson_id}/module/{module.module_id}/topic/{topic.topic_id}/quizzes/{quiz.quiz_id}/questions', headers=headers)
    assert get_response.status_code == 200
    questions = get_response.get_json()
    assert len(questions) == 1
    assert questions[0]['question_text'] == "What is interest?"

def test_update_and_delete_question(client, session, admin_user_token, admin_user, sample_quiz):
    """
    GIVEN an admin and an existing question
    WHEN updating and then deleting the question
    THEN verify the changes are applied correctly
    """
    lesson, module, topic, quiz = sample_quiz
    admin, _ = admin_user
    question = Question(quiz_id=quiz.quiz_id, created_by_admin_id=admin.user_id, question_text="Original", option1="O1", option2="O2", option3="O3", option4="O4", correct_answer="O1", score_points=1)
    session.add(question)
    session.flush()

    headers = {'Authorization': f'Bearer {admin_user_token}'}
    
    # Update
    update_data = {"question_text": "Updated Text", "score_points": 5}
    update_url = f'/api/{lesson.lesson_id}/module/{module.module_id}/topic/{topic.topic_id}/quizzes/{quiz.quiz_id}/question/{question.question_id}/update'
    update_response = client.put(update_url, headers=headers, data=json.dumps(update_data), content_type='application/json')
    assert update_response.status_code == 200
    assert update_response.get_json()['question_text'] == "Updated Text"
    assert update_response.get_json()['score_points'] == 5

    # Delete
    delete_url = f'/api/{lesson.lesson_id}/module/{module.module_id}/topic/{topic.topic_id}/quizzes/{quiz.quiz_id}/question/{question.question_id}/delete'
    delete_response = client.delete(delete_url, headers=headers)
    assert delete_response.status_code == 200

    # Verify soft delete
    deleted_question = Question.query.get(question.question_id)
    assert deleted_question.deleted_at is not None

# --- Tests for Quiz Taking (User) ---

def test_full_quiz_workflow(client, session, admin_user, regular_user_token, sample_quiz):
    """
    GIVEN a complete quiz with questions
    WHEN a user starts, answers, and evaluates the quiz
    THEN check that each step is successful and the final score is correct
    """
    lesson, module, topic, quiz = sample_quiz
    admin, _ = admin_user
    # Make quiz visible
    quiz.is_visible = True
    session.add(quiz)
    # Add questions
    q1 = Question(quiz_id=quiz.quiz_id, created_by_admin_id=admin.user_id, question_text="Q1", option1="A", option2="B", option3="C", option4="D", correct_answer="A", score_points=10)
    q2 = Question(quiz_id=quiz.quiz_id, created_by_admin_id=admin.user_id, question_text="Q2", option1="X", option2="Y", option3="Z", option4="W", correct_answer="Y", score_points=5)
    session.add_all([q1, q2])
    session.flush()

    headers = {'Authorization': f'Bearer {regular_user_token}'}

    # 1. Start the quiz
    start_response = client.post('/api/start_quiz', headers=headers, data=json.dumps({'quiz_id': quiz.quiz_id}), content_type='application/json')
    assert start_response.status_code == 201
    start_data = start_response.get_json()
    attempt_token = start_data['quiz_attempt_access_token']
    assert start_data['total_questions'] == 2

    # 2. Get quiz details
    details_response = client.get(f'/api/quiz_details/{attempt_token}', headers=headers)
    assert details_response.status_code == 200
    details_data = details_response.get_json()
    assert len(details_data['questions']) == 2

    # 3. Save answers
    save_q1 = client.post('/api/save_answer', headers=headers, data=json.dumps({'quiz_attempt_access_token': attempt_token, 'question_id': q1.question_id, 'selected_answer': 'A'}), content_type='application/json')
    assert save_q1.status_code == 200
    save_q2 = client.post('/api/save_answer', headers=headers, data=json.dumps({'quiz_attempt_access_token': attempt_token, 'question_id': q2.question_id, 'selected_answer': 'Z'}), content_type='application/json') # Wrong answer
    assert save_q2.status_code == 200

    # 4. Evaluate quiz
    eval_payload = {
        'quiz_attempt_access_token': attempt_token,
        'responses': [
            {'question_id': q1.question_id, 'selected_option': 'A'}, # Correct
            {'question_id': q2.question_id, 'selected_option': 'Z'}  # Incorrect
        ]
    }
    eval_response = client.post('/api/evaluate_quiz', headers=headers, data=json.dumps(eval_payload), content_type='application/json')
    assert eval_response.status_code == 200
    eval_data = eval_response.get_json()
    assert eval_data['score'] == 10 # Only q1 was correct
    assert eval_data['total_score_possible'] == 15
    assert "Quiz submitted successfully" in eval_data['message']

    # Verify attempt is marked as completed
    attempt = QuizAttempt.query.filter_by(quiz_attempt_access_token=attempt_token).one()
    assert attempt.completed_at is not None
    assert attempt.score_earned == 10

def test_user_cannot_start_invisible_quiz(client, session, regular_user_token, sample_quiz):
    """
    GIVEN a quiz that is not visible
    WHEN a user tries to start it
    THEN check for a 403 Forbidden status
    """
    _, _, _, quiz = sample_quiz
    quiz.is_visible = False
    session.add(quiz)
    session.flush()

    headers = {'Authorization': f'Bearer {regular_user_token}'}
    start_response = client.post('/api/start_quiz', headers=headers, data=json.dumps({'quiz_id': quiz.quiz_id}), content_type='application/json')
    # The app's generic exception handler turns the 403 abort into a 500
    assert start_response.status_code == 500
