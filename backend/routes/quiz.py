from flask import Blueprint, request
from flask_restx import Namespace, Resource, fields, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from model import db, Quiz, Question, User, Topic, Module, Lesson, QuizAttempt, QuestionAttempt, UserModuleProgress
from api_utils import get_current_ist
from datetime import datetime
import hashlib
from sqlalchemy.sql import func

# Define the Blueprint
quiz_bp = Blueprint('quiz', __name__)

# Define the quiz namespace
quiz_ns = Namespace('quiz', description='Quiz operations')

# Define request/response models
quiz_model = quiz_ns.model('Quiz', {
    'quiz_id': fields.Integer(description='Quiz ID'),
    'module_id': fields.Integer(description='Module ID'),
    'topic_id': fields.Integer(description='Topic ID'),
    'created_by_admin_id': fields.Integer(description='Admin ID who created the quiz'),
    'quiz_title': fields.String(description='Quiz title'),
    'duration_minutes': fields.Integer(description='Quiz duration in minutes'),
    'is_visible': fields.Boolean(description='Quiz visibility status'),
    'created_at': fields.DateTime(description='Creation date'),
    'updated_at': fields.DateTime(description='Last updated date')
})

quiz_model_with_stats = quiz_ns.model('QuizWithStats', {
    'quiz_id': fields.Integer(description='Quiz ID'),
    'module_id': fields.Integer(description='Module ID'),
    'topic_id': fields.Integer(description='Topic ID'),
    'quiz_title': fields.String(description='Quiz title'),
    'duration_minutes': fields.Integer(description='Quiz duration in minutes'),
    'is_visible': fields.Boolean(description='Quiz visibility status'),
    'created_at': fields.DateTime(description='Creation date'),
    'updated_at': fields.DateTime(description='Last updated date'),
    'total_questions': fields.Integer(description='Total number of questions in the quiz'),
    'total_score': fields.Integer(description='Total score possible for the quiz')
})


question_model = quiz_ns.model('Question', {
    'question_id': fields.Integer(description='Question ID'),
    'quiz_id': fields.Integer(description='Quiz ID'),
    'created_by_admin_id': fields.Integer(description='Admin ID who created the question'),
    'question_text': fields.String(description='Question text'),
    'option1': fields.String(description='Option 1'),
    'option2': fields.String(description='Option 2'),
    'option3': fields.String(description='Option 3'),
    'option4': fields.String(description='Option 4'),
    'correct_answer': fields.String(description='Correct answer'),
    'score_points': fields.Integer(description='Score points'),
    'created_at': fields.DateTime(description='Creation date'),
    'updated_at': fields.DateTime(description='Last updated date')
})

create_quiz_model = quiz_ns.model('CreateQuiz', {
    'quiz_title': fields.String(required=True, description='Quiz title'),
    'duration_minutes': fields.Integer(required=True, description='Quiz duration in minutes')
})

create_question_model = quiz_ns.model('CreateQuestion', {
    'question_text': fields.String(required=True, description='Question text'),
    'option1': fields.String(required=True, description='Option 1'),
    'option2': fields.String(required=True, description='Option 2'),
    'option3': fields.String(required=True, description='Option 3'),
    'option4': fields.String(required=True, description='Option 4'),
    'correct_answer': fields.String(required=True, description='Correct answer'),
    'score_points': fields.Integer(description='Score points', default=1)
})

update_question_model = quiz_ns.model('UpdateQuestion', {
    'question_text': fields.String(description='Question text'),
    'option1': fields.String(description='Option 1'),
    'option2': fields.String(description='Option 2'),
    'option3': fields.String(description='Option 3'),
    'option4': fields.String(description='Option 4'),
    'correct_answer': fields.String(description='Correct answer'),
    'score_points': fields.Integer(description='Score points')
})

success_model = quiz_ns.model('Success', {
    'message': fields.String(description='Success message')
})

error_model = quiz_ns.model('Error', {
    'error': fields.String(description='Error message')
})


# Model for the individual question details in the response
question_details_model = quiz_ns.model('QuestionDetails', {
    'question_id': fields.Integer,
    'question_text': fields.String,
    'option1': fields.String,
    'option2': fields.String,
    'option3': fields.String,
    'option4': fields.String,
    'score_points': fields.Integer,
    'selected_answer': fields.String(description='The user\'s previously saved answer for this question, if any.')
})

# Model for the main response of the new endpoint
quiz_details_response_model = quiz_ns.model('QuizDetailsResponse', {
    'quiz_title': fields.String,
    'duration_minutes': fields.Integer,
    'questions': fields.List(fields.Nested(question_details_model))
})



start_quiz_model = quiz_ns.model('StartQuiz', {
    'quiz_id': fields.Integer(required=True, description='Quiz ID')
})

start_quiz_response_model = quiz_ns.model('StartQuizResponse', {
    'message': fields.String(description='Success message'),
    'quiz_attempt_access_token': fields.String(description='Quiz attempt access token'),
    'total_questions': fields.Integer(description='Total number of questions in the quiz')
})

save_answer_model = quiz_ns.model('SaveAnswer', {
    'quiz_attempt_access_token': fields.String(required=True, description='Quiz attempt access token'),
    'question_id': fields.Integer(required=True, description='Question ID'),
    'selected_answer': fields.String(required=True, description='Selected answer')
})

# Define the nested model for responses in EvaluateQuiz
response_model = quiz_ns.model('Response', {
    'question_id': fields.Integer(required=True, description='Question ID'),
    'selected_option': fields.String(required=True, description='Selected option')
})

evaluate_quiz_model = quiz_ns.model('EvaluateQuiz', {
    'quiz_attempt_access_token': fields.String(required=True, description='Quiz attempt access token'),
    'responses': fields.List(fields.Nested(response_model))
})

evaluate_quiz_response = quiz_ns.model('EvaluateQuizResponse', {
    'score': fields.Float(description='Earned score'),
    'total_score_possible': fields.Float(description='Total possible score'),
    'message': fields.String(description='Success message')
})

@quiz_ns.route('/<int:lesson_id>/module/<int:module_id>/topic/<int:topic_id>/quizzes')
class QuizzesByTopic(Resource):
    @quiz_ns.doc('get_quizzes_by_topic', description='Retrieve all quizzes for a specific topic with question count and total score.', security='BearerAuth')
    @jwt_required()
    @quiz_ns.marshal_list_with(quiz_model_with_stats, code=200) # Use the new model
    @quiz_ns.response(401, 'Unauthorized: Missing or invalid token', error_model)
    @quiz_ns.response(403, 'Admin access required', error_model)
    @quiz_ns.response(404, 'Lesson, module, or topic not found', error_model)
    @quiz_ns.response(500, 'Unexpected error', error_model)
    def get(self, lesson_id, module_id, topic_id):
        """Retrieve all quizzes for a specific topic with question count and total score."""
        try:
            # --- User and path validation (remains the same) ---
            user_id = get_jwt_identity()
            user = User.query.filter_by(user_id=user_id).first()
            if not user:
                abort(403, 'Admin access required')

            lesson = Lesson.query.filter_by(lesson_id=lesson_id).first()
            if not lesson:
                abort(404, 'Lesson not found')

            module = Module.query.filter_by(module_id=module_id, lesson_id=lesson_id, deleted_at=None).first()
            if not module:
                abort(404, 'Module not found')

            topic = Topic.query.filter_by(topic_id=topic_id, module_id=module_id, deleted_at=None).first()
            if not topic:
                abort(404, 'Topic not found')

            # 1. Create a subquery for question count and total score
            question_stats = db.session.query(
                Question.quiz_id,
                func.count(Question.question_id).label('total_questions'),
                func.sum(Question.score_points).label('total_score')
            ).filter(Question.deleted_at.is_(None)).group_by(Question.quiz_id).subquery()

            # 2. Join the Quiz query with the subquery
            quizzes_with_stats = db.session.query(
                Quiz,
                question_stats.c.total_questions,
                question_stats.c.total_score
            ).outerjoin(
                question_stats, Quiz.quiz_id == question_stats.c.quiz_id
            ).filter(
                Quiz.topic_id == topic_id,
                Quiz.deleted_at.is_(None)
            ).all()

            # 3. Format the response data
            results = []
            for quiz, total_questions, total_score in quizzes_with_stats:
                results.append({
                    'quiz_id': quiz.quiz_id,
                    'module_id': quiz.module_id,
                    'topic_id': quiz.topic_id,
                    'quiz_title': quiz.quiz_title,
                    'duration_minutes': quiz.duration_minutes,
                    'is_visible': quiz.is_visible,
                    'created_at': quiz.created_at,
                    'updated_at': quiz.updated_at,
                    'total_questions': total_questions or 0,
                    'total_score': int(total_score) if total_score is not None else 0
                })
            
            return results, 200

        except Exception as e:
            abort(500, f'An unexpected error occurred: {str(e)}')
        
@quiz_ns.route('/<int:lesson_id>/module/<int:module_id>/topic/<int:topic_id>/quiz/create')
class CreateQuiz(Resource):
    @quiz_ns.doc('create_quiz', description='Create a new quiz for a topic.', security='BearerAuth')
    @jwt_required()
    @quiz_ns.expect(create_quiz_model)
    @quiz_ns.marshal_with(quiz_model, code=201)
    @quiz_ns.response(400, 'Invalid input', error_model)
    @quiz_ns.response(401, 'Unauthorized: Missing or invalid token', error_model)
    @quiz_ns.response(403, 'Admin access required', error_model)
    @quiz_ns.response(404, 'Lesson, module, or topic not found', error_model)
    @quiz_ns.response(500, 'Unexpected error', error_model)
    def post(self, lesson_id, module_id, topic_id):
        """Create a new quiz for a topic."""
        try:
            user_id = get_jwt_identity()
            user = User.query.filter_by(user_id=user_id).first()
            if not user or user.user_role != 'admin':
                abort(403, 'Admin access required')

            lesson = Lesson.query.filter_by(lesson_id=lesson_id).first()
            if not lesson:
                abort(404, 'Lesson not found')

            module = Module.query.filter_by(module_id=module_id, lesson_id=lesson_id, deleted_at=None).first()
            if not module:
                abort(404, 'Module not found')

            topic = Topic.query.filter_by(topic_id=topic_id, module_id=module_id, deleted_at=None).first()
            if not topic:
                abort(404, 'Topic not found')

            data = quiz_ns.payload
            if not data.get('quiz_title') or not data.get('duration_minutes'):
                abort(400, 'Quiz title and duration are required')
            if data['duration_minutes'] <= 0:
                abort(400, 'Duration must be positive')

            new_quiz = Quiz(
                module_id=module_id,
                topic_id=topic_id,
                created_by_admin_id=user_id,
                quiz_title=data['quiz_title'],
                duration_minutes=data['duration_minutes'],
                created_at=get_current_ist(),
                updated_at=get_current_ist()
            )
            db.session.add(new_quiz)
            db.session.commit()

            return {
                'quiz_id': new_quiz.quiz_id,
                'module_id': new_quiz.module_id,
                'topic_id': new_quiz.topic_id,
                'created_by_admin_id': new_quiz.created_by_admin_id,
                'quiz_title': new_quiz.quiz_title,
                'duration_minutes': new_quiz.duration_minutes,
                'is_visible': new_quiz.is_visible,
                'created_at': new_quiz.created_at,
                'updated_at': new_quiz.updated_at
            }, 201
        except Exception as e:
            db.session.rollback()
            abort(500, f'An unexpected error occurred: {str(e)}')

@quiz_ns.route('/<int:lesson_id>/module/<int:module_id>/topic/<int:topic_id>/quizzes/<int:quiz_id>/visibility')
class UpdateQuizVisibility(Resource):
    @quiz_ns.doc('update_quiz_visibility', description='Update quiz visibility.', security='BearerAuth')
    @jwt_required()
    @quiz_ns.expect({'is_visible': fields.Boolean(required=True, description='Visibility status')})
    @quiz_ns.marshal_with(quiz_model, code=200)
    @quiz_ns.response(401, 'Unauthorized: Missing or invalid token', error_model)
    @quiz_ns.response(403, 'Admin access required', error_model)
    @quiz_ns.response(404, 'Lesson, module, topic, or quiz not found', error_model)
    @quiz_ns.response(500, 'Unexpected error', error_model)
    def put(self, lesson_id, module_id, topic_id, quiz_id):
        """Update quiz visibility."""
        try:
            user_id = get_jwt_identity()
            user = User.query.filter_by(user_id=user_id).first()
            if not user or user.user_role != 'admin':
                abort(403, 'Admin access required')

            lesson = Lesson.query.filter_by(lesson_id=lesson_id).first()
            if not lesson:
                abort(404, 'Lesson not found')

            module = Module.query.filter_by(module_id=module_id, lesson_id=lesson_id, deleted_at=None).first()
            if not module:
                abort(404, 'Module not found')

            topic = Topic.query.filter_by(topic_id=topic_id, module_id=module_id, deleted_at=None).first()
            if not topic:
                abort(404, 'Topic not found')

            quiz = Quiz.query.filter_by(quiz_id=quiz_id, module_id=module_id, topic_id=topic_id, deleted_at=None).first()
            if not quiz:
                abort(404, 'Quiz not found')

            data = quiz_ns.payload
            quiz.is_visible = data['is_visible']
            quiz.updated_at = get_current_ist()
            db.session.commit()

            return {
                'quiz_id': quiz.quiz_id,
                'module_id': quiz.module_id,
                'topic_id': quiz.topic_id,
                'created_by_admin_id': quiz.created_by_admin_id,
                'quiz_title': quiz.quiz_title,
                'duration_minutes': quiz.duration_minutes,
                'is_visible': quiz.is_visible,
                'created_at': quiz.created_at,
                'updated_at': quiz.updated_at
            }, 200
        except Exception as e:
            db.session.rollback()
            abort(500, f'An unexpected error occurred: {str(e)}')

@quiz_ns.route('/<int:lesson_id>/module/<int:module_id>/topic/<int:topic_id>/quizzes/<int:quiz_id>/delete')
class DeleteQuiz(Resource):
    @quiz_ns.doc('delete_quiz', description='Delete a quiz (soft delete).', security='BearerAuth')
    @jwt_required()
    @quiz_ns.marshal_with(success_model, code=200)
    @quiz_ns.response(401, 'Unauthorized: Missing or invalid token', error_model)
    @quiz_ns.response(403, 'Admin access required', error_model)
    @quiz_ns.response(404, 'Lesson, module, topic, or quiz not found', error_model)
    @quiz_ns.response(500, 'Unexpected error', error_model)
    def delete(self, lesson_id, module_id, topic_id, quiz_id):
        """Delete a quiz (soft delete)."""
        try:
            user_id = get_jwt_identity()
            user = User.query.filter_by(user_id=user_id).first()
            if not user or user.user_role != 'admin':
                abort(403, 'Admin access required')

            lesson = Lesson.query.filter_by(lesson_id=lesson_id).first()
            if not lesson:
                abort(404, 'Lesson not found')

            module = Module.query.filter_by(module_id=module_id, lesson_id=lesson_id, deleted_at=None).first()
            if not module:
                abort(404, 'Module not found')

            topic = Topic.query.filter_by(topic_id=topic_id, module_id=module_id, deleted_at=None).first()
            if not topic:
                abort(404, 'Topic not found')

            quiz = Quiz.query.filter_by(quiz_id=quiz_id, module_id=module_id, topic_id=topic_id, deleted_at=None).first()
            if not quiz:
                abort(404, 'Quiz not found')

            quiz.deleted_at = get_current_ist()
            db.session.commit()

            return {'message': 'Quiz deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            abort(500, f'An unexpected error occurred: {str(e)}')

@quiz_ns.route('/<int:lesson_id>/module/<int:module_id>/topic/<int:topic_id>/quizzes/<int:quiz_id>/questions')
class QuestionsByQuiz(Resource):
    @quiz_ns.doc('get_questions_by_quiz', description='Retrieve all questions for a specific quiz.', security='BearerAuth')
    @jwt_required()
    @quiz_ns.marshal_list_with(question_model, code=200)
    @quiz_ns.response(401, 'Unauthorized: Missing or invalid token', error_model)
    @quiz_ns.response(403, 'User not found or access denied', error_model)
    @quiz_ns.response(404, 'Lesson, module, topic, or quiz not found', error_model)
    @quiz_ns.response(500, 'Unexpected error', error_model)
    def get(self, lesson_id, module_id, topic_id, quiz_id):
        """Retrieve all questions for a specific quiz."""
        try:
            user_id = get_jwt_identity()
            user = User.query.filter_by(user_id=user_id).first()
            if not user:
                abort(403, 'User not found or access denied')

            lesson = Lesson.query.filter_by(lesson_id=lesson_id).first()
            if not lesson:
                abort(404, 'Lesson not found')

            module = Module.query.filter_by(module_id=module_id, lesson_id=lesson_id, deleted_at=None).first()
            if not module:
                abort(404, 'Module not found')

            topic = Topic.query.filter_by(topic_id=topic_id, module_id=module_id, deleted_at=None).first()
            if not topic:
                abort(404, 'Topic not found')

            quiz = Quiz.query.filter_by(quiz_id=quiz_id, module_id=module_id, topic_id=topic_id, deleted_at=None).first()
            if not quiz:
                abort(404, 'Quiz not found')

            questions = Question.query.filter_by(quiz_id=quiz_id, deleted_at=None).all()
            return [{
                'question_id': q.question_id,
                'quiz_id': q.quiz_id,
                'created_by_admin_id': q.created_by_admin_id,
                'question_text': q.question_text,
                'option1': q.option1,
                'option2': q.option2,
                'option3': q.option3,
                'option4': q.option4,
                'correct_answer': q.correct_answer,
                'score_points': q.score_points,
                'created_at': q.created_at,
                'updated_at': q.updated_at
            } for q in questions], 200
        except Exception as e:
            abort(500, f'An unexpected error occurred: {str(e)}')

@quiz_ns.route('/<int:lesson_id>/module/<int:module_id>/topic/<int:topic_id>/quizzes/<int:quiz_id>/question/create')
class CreateQuestion(Resource):
    @quiz_ns.doc('create_question', description='Create a new question for a quiz.', security='BearerAuth')
    @jwt_required()
    @quiz_ns.expect(create_question_model)
    @quiz_ns.marshal_with(question_model, code=201)
    @quiz_ns.response(400, 'Invalid input', error_model)
    @quiz_ns.response(401, 'Unauthorized: Missing or invalid token', error_model)
    @quiz_ns.response(403, 'Admin access required', error_model)
    @quiz_ns.response(404, 'Lesson, module, topic, or quiz not found', error_model)
    @quiz_ns.response(500, 'Unexpected error', error_model)
    def post(self, lesson_id, module_id, topic_id, quiz_id):
        """Create a new question for a quiz."""
        try:
            user_id = get_jwt_identity()
            user = User.query.filter_by(user_id=user_id).first()
            if not user or user.user_role != 'admin':
                abort(403, 'Admin access required')

            lesson = Lesson.query.filter_by(lesson_id=lesson_id).first()
            if not lesson:
                abort(404, 'Lesson not found')

            module = Module.query.filter_by(module_id=module_id, lesson_id=lesson_id, deleted_at=None).first()
            if not module:
                abort(404, 'Module not found')

            topic = Topic.query.filter_by(topic_id=topic_id, module_id=module_id, deleted_at=None).first()
            if not topic:
                abort(404, 'Topic not found')

            quiz = Quiz.query.filter_by(quiz_id=quiz_id, module_id=module_id, topic_id=topic_id, deleted_at=None).first()
            if not quiz:
                abort(404, 'Quiz not found')

            data = quiz_ns.payload
            required_fields = ['question_text', 'option1', 'option2', 'option3', 'option4', 'correct_answer']
            if not all(k in data for k in required_fields):
                abort(400, 'All question fields are required')

            if data['correct_answer'] not in [data['option1'], data['option2'], data['option3'], data['option4']]:
                abort(400, 'Correct answer must be one of the provided options')

            if 'score_points' in data and data['score_points'] <= 0:
                abort(400, 'Score points must be positive')

            new_question = Question(
                quiz_id=quiz_id,
                created_by_admin_id=user_id,
                question_text=data['question_text'],
                option1=data['option1'],
                option2=data['option2'],
                option3=data['option3'],
                option4=data['option4'],
                correct_answer=data['correct_answer'],
                score_points=data.get('score_points', 1),
                created_at=get_current_ist(),
                updated_at=get_current_ist()
            )
            db.session.add(new_question)
            db.session.commit()

            return {
                'question_id': new_question.question_id,
                'quiz_id': new_question.quiz_id,
                'created_by_admin_id': new_question.created_by_admin_id,
                'question_text': new_question.question_text,
                'option1': new_question.option1,
                'option2': new_question.option2,
                'option3': new_question.option3,
                'option4': new_question.option4,
                'correct_answer': new_question.correct_answer,
                'score_points': new_question.score_points,
                'created_at': new_question.created_at,
                'updated_at': new_question.updated_at
            }, 201
        except Exception as e:
            db.session.rollback()
            abort(500, f'An unexpected error occurred: {str(e)}')

@quiz_ns.route('/<int:lesson_id>/module/<int:module_id>/topic/<int:topic_id>/quizzes/<int:quiz_id>/question/<int:question_id>/update')
class UpdateQuestion(Resource):
    @quiz_ns.doc('update_question', description='Update a question.', security='BearerAuth')
    @jwt_required()
    @quiz_ns.expect(update_question_model)
    @quiz_ns.marshal_with(question_model, code=200)
    @quiz_ns.response(400, 'Invalid input', error_model)
    @quiz_ns.response(401, 'Unauthorized: Missing or invalid token', error_model)
    @quiz_ns.response(403, 'Admin access required', error_model)
    @quiz_ns.response(404, 'Lesson, module, topic, quiz, or question not found', error_model)
    @quiz_ns.response(500, 'Unexpected error', error_model)
    def put(self, lesson_id, module_id, topic_id, quiz_id, question_id):
        """Update a question."""
        try:
            user_id = get_jwt_identity()
            user = User.query.filter_by(user_id=user_id).first()
            if not user or user.user_role != 'admin':
                abort(403, 'Admin access required')

            lesson = Lesson.query.filter_by(lesson_id=lesson_id).first()
            if not lesson:
                abort(404, 'Lesson not found')

            module = Module.query.filter_by(module_id=module_id, lesson_id=lesson_id, deleted_at=None).first()
            if not module:
                abort(404, 'Module not found')

            topic = Topic.query.filter_by(topic_id=topic_id, module_id=module_id, deleted_at=None).first()
            if not topic:
                abort(404, 'Topic not found')

            quiz = Quiz.query.filter_by(quiz_id=quiz_id, module_id=module_id, topic_id=topic_id, deleted_at=None).first()
            if not quiz:
                abort(404, 'Quiz not found')

            question = Question.query.filter_by(question_id=question_id, quiz_id=quiz_id, deleted_at=None).first()
            if not question:
                abort(404, 'Question not found')

            data = quiz_ns.payload
            if not data:
                abort(400, 'No update data provided')

            if 'question_text' in data:
                question.question_text = data['question_text']
            if 'option1' in data:
                question.option1 = data['option1']
            if 'option2' in data:
                question.option2 = data['option2']
            if 'option3' in data:
                question.option3 = data['option3']
            if 'option4' in data:
                question.option4 = data['option4']
            if 'correct_answer' in data:
                if data['correct_answer'] not in [data.get('option1', question.option1), 
                                                data.get('option2', question.option2), 
                                                data.get('option3', question.option3), 
                                                data.get('option4', question.option4)]:
                    abort(400, 'Correct answer must be one of the provided options')
                question.correct_answer = data['correct_answer']
            if 'score_points' in data:
                if data['score_points'] <= 0:
                    abort(400, 'Score points must be positive')
                question.score_points = data['score_points']

            question.updated_at = get_current_ist()
            db.session.commit()

            return {
                'question_id': question.question_id,
                'quiz_id': question.quiz_id,
                'created_by_admin_id': question.created_by_admin_id,
                'question_text': question.question_text,
                'option1': question.option1,
                'option2': question.option2,
                'option3': question.option3,
                'option4': question.option4,
                'correct_answer': question.correct_answer,
                'score_points': question.score_points,
                'created_at': question.created_at,
                'updated_at': question.updated_at
            }, 200
        except Exception as e:
            db.session.rollback()
            abort(500, f'An unexpected error occurred: {str(e)}')

@quiz_ns.route('/<int:lesson_id>/module/<int:module_id>/topic/<int:topic_id>/quizzes/<int:quiz_id>/question/<int:question_id>/delete')
class DeleteQuestion(Resource):
    @quiz_ns.doc('delete_question', description='Delete a question (soft delete).', security='BearerAuth')
    @jwt_required()
    @quiz_ns.marshal_with(success_model, code=200)
    @quiz_ns.response(401, 'Unauthorized: Missing or invalid token', error_model)
    @quiz_ns.response(403, 'Admin access required', error_model)
    @quiz_ns.response(404, 'Lesson, module, topic, quiz, or question not found', error_model)
    @quiz_ns.response(500, 'Unexpected error', error_model)
    def delete(self, lesson_id, module_id, topic_id, quiz_id, question_id):
        """Delete a question (soft delete)."""
        try:
            user_id = get_jwt_identity()
            user = User.query.filter_by(user_id=user_id).first()
            if not user or user.user_role != 'admin':
                abort(403, 'Admin access required')

            lesson = Lesson.query.filter_by(lesson_id=lesson_id).first()
            if not lesson:
                abort(404, 'Lesson not found')

            module = Module.query.filter_by(module_id=module_id, lesson_id=lesson_id, deleted_at=None).first()
            if not module:
                abort(404, 'Module not found')

            topic = Topic.query.filter_by(topic_id=topic_id, module_id=module_id, deleted_at=None).first()
            if not topic:
                abort(404, 'Topic not found')

            quiz = Quiz.query.filter_by(quiz_id=quiz_id, module_id=module_id, topic_id=topic_id, deleted_at=None).first()
            if not quiz:
                abort(404, 'Quiz not found')

            question = Question.query.filter_by(question_id=question_id, quiz_id=quiz_id, deleted_at=None).first()
            if not question:
                abort(404, 'Question not found')

            question.deleted_at = get_current_ist()
            db.session.commit()

            return {'message': 'Question deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            abort(500, f'An unexpected error occurred: {str(e)}')


# --- API Endpoint ---
@quiz_ns.route('/quiz_details/<string:access_token>')
@quiz_ns.param('access_token', 'The access token for a specific quiz attempt.')
class QuizDetails(Resource):
    @quiz_ns.doc('get_quiz_details', description='Fetches all necessary details to render a quiz page for a specific attempt.', security='BearerAuth')
    @jwt_required()
    @quiz_ns.marshal_with(quiz_details_response_model, code=200)
    @quiz_ns.response(401, 'Unauthorized', error_model)
    @quiz_ns.response(403, 'Quiz attempt not accessible by this user', error_model)
    @quiz_ns.response(404, 'Quiz attempt not found', error_model)
    @quiz_ns.response(500, 'Unexpected error', error_model)
    def get(self, access_token):
        """Fetch details for a specific quiz attempt."""
        try:
            user_id = get_jwt_identity()
            # 1. Find the quiz attempt using the access token
            attempt = QuizAttempt.query.filter_by(quiz_attempt_access_token=access_token).first()
            if not attempt:
                abort(404, 'Quiz attempt not found.')
            
            # 3. Check if the quiz is already completed
            if attempt.completed_at:
                abort(400, 'This quiz has already been completed.')

            # 4. Fetch the main quiz details
            quiz = Quiz.query.get(attempt.quiz_id)
            if not quiz or not quiz.is_visible or quiz.deleted_at:
                abort(404, 'The associated quiz is no longer available.')

            # 5. Fetch all questions for this quiz
            questions = Question.query.filter_by(quiz_id=quiz.quiz_id, deleted_at=None).all()
            
            # 6. Fetch all *existing* answers for this attempt to pre-fill the UI
            # This creates a dictionary for quick lookups: {question_id: selected_answer}
            saved_answers = {
                qa.question_id: qa.selected_answer
                for qa in QuestionAttempt.query.filter_by(attempt_id=attempt.attempt_id).all()
            }

            # 7. Structure the response
            response_questions = []
            for q in questions:
                response_questions.append({
                    'question_id': q.question_id,
                    'question_text': q.question_text,
                    'option1': q.option1,
                    'option2': q.option2,
                    'option3': q.option3,
                    'option4': q.option4,
                    'score_points': q.score_points,
                    # Look up the saved answer for this question. If not found, it will be null.
                    'selected_answer': saved_answers.get(q.question_id)
                })

            return {
                'quiz_title': quiz.quiz_title,
                'duration_minutes': quiz.duration_minutes,
                'questions': response_questions
            }, 200

        except Exception as e:
            # It's good practice to log the actual error for debugging
            print(f"Error in /quiz_details: {e}") 
            abort(500, f'An unexpected error occurred: {str(e)}')


@quiz_ns.route('/start_quiz')
class StartQuiz(Resource):
    @quiz_ns.doc('start_quiz', description='Start a new quiz attempt.', security='BearerAuth')
    @jwt_required()
    @quiz_ns.expect(start_quiz_model)
    @quiz_ns.marshal_with(start_quiz_response_model, code=201)
    @quiz_ns.response(400, 'Invalid input', error_model)
    @quiz_ns.response(401, 'Unauthorized', error_model)
    @quiz_ns.response(403, 'Quiz not accessible', error_model)
    @quiz_ns.response(404, 'Quiz, topic, module, or lesson not found', error_model)
    @quiz_ns.response(500, 'Unexpected error', error_model)
    def post(self):
        """Start a new quiz attempt."""
        try:
            user_id = get_jwt_identity()
            user = User.query.filter_by(user_id=user_id).first()
            if not user:
                abort(401, 'User not found')

            data = quiz_ns.payload
            quiz = Quiz.query.filter_by(quiz_id=data['quiz_id'], deleted_at=None).first()
            if not quiz:
                abort(404, 'Quiz not found')
            if not quiz.is_visible:
                abort(403, 'Quiz is not accessible')

            # Fetch related module, topic, and lesson
            module = Module.query.filter_by(module_id=quiz.module_id, deleted_at=None).first()
            if not module:
                abort(404, 'Module not found')
            topic = Topic.query.filter_by(topic_id=quiz.topic_id, deleted_at=None).first()
            if not topic:
                abort(404, 'Topic not found')
            lesson = Lesson.query.filter_by(lesson_id=module.lesson_id).first()
            if not lesson:
                abort(404, 'Lesson not found')

            # Check user progress
            progress = UserModuleProgress.query.filter_by(user_id=user_id, module_id=module.module_id, topic_id=topic.topic_id).first()
            if not progress:
                progress = UserModuleProgress(
                    user_id=user_id,
                    module_id=module.module_id,
                    topic_id=topic.topic_id,
                    started_at=get_current_ist(),
                    last_accessed_at=get_current_ist(),
                    progress_percentage=0
                )
                db.session.add(progress)
            else:
                progress.last_accessed_at = get_current_ist()
            db.session.commit()

            # Generate quiz_attempt_access_token
            timestamp = get_current_ist().strftime('%Y%m%d%H%M%S')
            token_base = f"{timestamp}_{user_id}_{data['quiz_id']}_{topic.topic_id}_{module.module_id}_{lesson.lesson_id}"
            quiz_attempt_access_token = hashlib.sha256(token_base.encode()).hexdigest()

            total_questions = Question.query.filter_by(quiz_id=data['quiz_id'], deleted_at=None).count()
            total_score_possible = Question.query.filter_by(quiz_id=data['quiz_id'], deleted_at=None).with_entities(func.sum(Question.score_points)).scalar() or 0

            attempt = QuizAttempt(
                user_id=user_id,
                quiz_id=data['quiz_id'],
                quiz_attempt_access_token=quiz_attempt_access_token,
                total_questions=total_questions,
                total_score_possible=total_score_possible,
                started_at=get_current_ist()
            )
            db.session.add(attempt)
            db.session.commit()

            return {
                'message': 'Quiz started',
                'quiz_attempt_access_token': quiz_attempt_access_token,
                'total_questions': total_questions
            }, 201
        except Exception as e:
            db.session.rollback()
            abort(500, f'An unexpected error occurred: {str(e)}')

@quiz_ns.route('/save_answer')
class SaveAnswer(Resource):
    @quiz_ns.doc('save_answer', description='Save or update user answer.', security='BearerAuth')
    @jwt_required()
    @quiz_ns.expect(save_answer_model)
    @quiz_ns.marshal_with(success_model, code=200)
    @quiz_ns.response(400, 'Invalid input', error_model)
    @quiz_ns.response(401, 'Unauthorized', error_model)
    @quiz_ns.response(403, 'Quiz attempt not accessible', error_model)
    @quiz_ns.response(404, 'Attempt or question not found', error_model)
    @quiz_ns.response(500, 'Unexpected error', error_model)
    def post(self):
        """Save or update user answer."""
        user_id = get_jwt_identity()
        data = quiz_ns.payload
        # print(f"Received data: {data}, User ID: {user_id}")
        if not data or not all(key in data for key in ['quiz_attempt_access_token', 'question_id', 'selected_answer']):
            abort(400, 'Missing required fields')

        # Fetch the quiz attempt by access token
        attempt = QuizAttempt.query.filter_by(quiz_attempt_access_token=data['quiz_attempt_access_token']).first()
        if not attempt:
            abort(404, 'Quiz attempt not found')

        if attempt.completed_at:
            # print(f"Quiz attempt already completed: {attempt.completed_at}")
            abort(403, 'Quiz attempt already completed')

        # print(f"Attempt found: {attempt.quiz_attempt_access_token}, User ID: {attempt.user_id}")
        question = Question.query.filter_by(question_id=data['question_id'], quiz_id=attempt.quiz_id, deleted_at=None).first()
        if not question:
            abort(404, 'Question not found')
        
        # print(f"Selected answer: {data['selected_answer']}, Correct answer: {question.correct_answer}")
        if data['selected_answer'] not in [question.option1, question.option2, question.option3, question.option4]:
            abort(400, 'Selected answer must be one of the provided options')
        
        # === The try block should only protect the database transaction ===
        # print(f"Processing answer for question ID: {data['question_id']}, Selected answer: {data['selected_answer']}")
        try:
            # Update or create question attempt
            existing_attempt = QuestionAttempt.query.filter_by(attempt_id=attempt.attempt_id, question_id=data['question_id']).first()
            if existing_attempt:
                existing_attempt.selected_answer = data['selected_answer']
                existing_attempt.is_correct = (data['selected_answer'] == question.correct_answer)
                existing_attempt.attempted_at = get_current_ist()
            else:
                new_attempt = QuestionAttempt(
                    attempt_id=attempt.attempt_id,
                    user_id=user_id,
                    question_id=data['question_id'],
                    selected_answer=data['selected_answer'],
                    is_correct=(data['selected_answer'] == question.correct_answer),
                    attempted_at=get_current_ist()
                )
                db.session.add(new_attempt)

            db.session.commit()
            return {'message': 'Answer saved successfully'}, 200
        except Exception as e:
            db.session.rollback()
            abort(500, f'An unexpected error occurred: {str(e)}')
@quiz_ns.route('/evaluate_quiz')
class EvaluateQuiz(Resource):
    @quiz_ns.doc('evaluate_quiz', description='Evaluate and submit quiz.', security='BearerAuth')
    @jwt_required()
    @quiz_ns.expect(evaluate_quiz_model)
    @quiz_ns.marshal_with(evaluate_quiz_response, code=200)
    @quiz_ns.response(400, 'Invalid input', error_model)
    @quiz_ns.response(401, 'Unauthorized', error_model)
    @quiz_ns.response(403, 'Quiz attempt not accessible', error_model)
    @quiz_ns.response(404, 'Attempt or question not found', error_model)
    @quiz_ns.response(500, 'Unexpected error', error_model)
    def post(self):
        """Evaluate and submit quiz."""
        try:
            user_id = get_jwt_identity()
            data = quiz_ns.payload
            attempt = QuizAttempt.query.filter_by(quiz_attempt_access_token=data['quiz_attempt_access_token']).first()
            if not attempt:
                abort(404, 'Quiz attempt not found')

            if attempt.completed_at:
                abort(400, 'Quiz already submitted')

            # Validate all questions are answered
            total_questions = Question.query.filter_by(quiz_id=attempt.quiz_id, deleted_at=None).count()
            total_score = 0
            question_ids = set()
            for response in data['responses']:
                if response['question_id'] in question_ids:
                    abort(400, 'Duplicate question ID in responses')
                question_ids.add(response['question_id'])

                question = Question.query.filter_by(question_id=response['question_id'], quiz_id=attempt.quiz_id, deleted_at=None).first()
                if not question:
                    abort(404, f'Question {response["question_id"]} not found')
                if response['selected_option'] not in [question.option1, question.option2, question.option3, question.option4]:
                    abort(400, f'Invalid option for question {response["question_id"]}')

                # Save or update question attempt
                existing_attempt = QuestionAttempt.query.filter_by(attempt_id=attempt.attempt_id, question_id=response['question_id']).first()
                if existing_attempt:
                    existing_attempt.selected_answer = response['selected_option']
                    existing_attempt.is_correct = (response['selected_option'] == question.correct_answer)
                    existing_attempt.attempted_at = get_current_ist()
                else:
                    new_attempt = QuestionAttempt(
                        attempt_id=attempt.attempt_id,
                        user_id=user_id,
                        question_id=response['question_id'],
                        selected_answer=response['selected_option'],
                        is_correct=(response['selected_option'] == question.correct_answer),
                        attempted_at=get_current_ist()
                    )
                    db.session.add(new_attempt)

                if response['selected_option'] == question.correct_answer:
                    total_score += question.score_points

            # Update progress
            progress = UserModuleProgress.query.filter_by(user_id=user_id, module_id=attempt.quiz.module_id, topic_id=attempt.quiz.topic_id).first()
            if progress:
                progress.progress_percentage = min(100, progress.progress_percentage + (100 / total_questions))
                progress.last_accessed_at = get_current_ist()
                if progress.progress_percentage >= 100:
                    progress.completed_at = get_current_ist()

            attempt.score_earned = total_score
            attempt.completed_at = get_current_ist()
            
            # --- CORRECTION FOR TypeError ---
            # The original code caused a TypeError because it tried to subtract
            # an offset-naive datetime (started_at) from an offset-aware one (completed_at).
            # The fix is to make both datetimes naive before the subtraction,
            # assuming they are both in the same timezone.
            if attempt.completed_at and attempt.started_at:
                # Convert the aware datetime to naive by removing timezone info
                completed_at_naive = attempt.completed_at.replace(tzinfo=None)
                # Now both datetimes are naive, so subtraction is safe
                attempt.time_taken_seconds = (completed_at_naive - attempt.started_at).total_seconds()
            else:
                attempt.time_taken_seconds = 0
            # --- END CORRECTION ---

            db.session.commit()

            return {
                'score': total_score,
                'total_score_possible': attempt.total_score_possible,
                'message': 'Quiz submitted successfully'
            }, 200
        except Exception as e:
            db.session.rollback()
            # Log the full exception for debugging
            print(f"Error in /evaluate_quiz: {e}")
            import traceback
            traceback.print_exc()
            abort(500, f'An unexpected error occurred: {str(e)}')


# Register the namespace with the Blueprint
quiz_ns.add_resource(QuizzesByTopic, '/<int:lesson_id>/module/<int:module_id>/topic/<int:topic_id>/quizzes')
quiz_ns.add_resource(CreateQuiz, '/<int:lesson_id>/module/<int:module_id>/topic/<int:topic_id>/quiz/create')
quiz_ns.add_resource(UpdateQuizVisibility, '/<int:lesson_id>/module/<int:module_id>/topic/<int:topic_id>/quizzes/<int:quiz_id>/visibility')
quiz_ns.add_resource(DeleteQuiz, '/<int:lesson_id>/module/<int:module_id>/topic/<int:topic_id>/quizzes/<int:quiz_id>/delete')
quiz_ns.add_resource(QuestionsByQuiz, '/<int:lesson_id>/module/<int:module_id>/topic/<int:topic_id>/quizzes/<int:quiz_id>/questions')
quiz_ns.add_resource(CreateQuestion, '/<int:lesson_id>/module/<int:module_id>/topic/<int:topic_id>/quizzes/<int:quiz_id>/question/create')
quiz_ns.add_resource(UpdateQuestion, '/<int:lesson_id>/module/<int:module_id>/topic/<int:topic_id>/quizzes/<int:quiz_id>/question/<int:question_id>/update')
quiz_ns.add_resource(DeleteQuestion, '/<int:lesson_id>/module/<int:module_id>/topic/<int:topic_id>/quizzes/<int:quiz_id>/question/<int:question_id>/delete')
quiz_ns.add_resource(QuizDetails, '/quiz_details/<string:access_token>')
quiz_ns.add_resource(StartQuiz, '/start_quiz')
quiz_ns.add_resource(SaveAnswer, '/save_answer')
quiz_ns.add_resource(EvaluateQuiz, '/evaluate_quiz')