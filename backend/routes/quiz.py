from flask import Blueprint, request
from flask_restx import Namespace, Resource, fields, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from model import db, Quiz, Question, User, Topic, Module, Lesson
from api_utils import get_current_ist
from datetime import datetime

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
    'correct_answer': fields.String(required=True, description='Correct answer')
})

update_question_model = quiz_ns.model('UpdateQuestion', {
    'question_text': fields.String(description='Question text'),
    'option1': fields.String(description='Option 1'),
    'option2': fields.String(description='Option 2'),
    'option3': fields.String(description='Option 3'),
    'option4': fields.String(description='Option 4'),
    'correct_answer': fields.String(description='Correct answer')
})

success_model = quiz_ns.model('Success', {
    'message': fields.String(description='Success message')
})

error_model = quiz_ns.model('Error', {
    'error': fields.String(description='Error message')
})

@quiz_ns.route('/<int:lesson_id>/module/<int:module_id>/topic/<int:topic_id>/quizzes')
class QuizzesByTopic(Resource):
    @quiz_ns.doc('get_quizzes_by_topic', description='Retrieve all quizzes for a specific topic.', security='BearerAuth')
    @jwt_required()
    @quiz_ns.marshal_list_with(quiz_model, code=200)
    @quiz_ns.response(401, 'Unauthorized: Missing or invalid token', error_model)
    @quiz_ns.response(404, 'Lesson, module, or topic not found', error_model)
    @quiz_ns.response(500, 'Unexpected error', error_model)
    def get(self, lesson_id, module_id, topic_id):
        """Retrieve all quizzes for a specific topic."""
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

            quizzes = Quiz.query.filter_by(topic_id=topic_id, deleted_at=None).all()
            return [{
                'quiz_id': quiz.quiz_id,
                'module_id': quiz.module_id,
                'topic_id': quiz.topic_id,
                'created_by_admin_id': quiz.created_by_admin_id,
                'quiz_title': quiz.quiz_title,
                'duration_minutes': quiz.duration_minutes,
                'is_visible': quiz.is_visible,
                'created_at': quiz.created_at,
                'updated_at': quiz.updated_at
            } for quiz in quizzes], 200

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

@quiz_ns.route('/<int:lesson_id>/module/<int:module_id>/topic/quizzes/<int:quiz_id>/visibility')
class UpdateQuizVisibility(Resource):
    @quiz_ns.doc('update_quiz_visibility', description='Update quiz visibility.', security='BearerAuth')
    @jwt_required()
    @quiz_ns.expect({'is_visible': fields.Boolean(required=True, description='Visibility status')})
    @quiz_ns.marshal_with(quiz_model, code=200)
    @quiz_ns.response(401, 'Unauthorized: Missing or invalid token', error_model)
    @quiz_ns.response(403, 'Admin access required', error_model)
    @quiz_ns.response(404, 'Lesson, module, topic, or quiz not found', error_model)
    @quiz_ns.response(500, 'Unexpected error', error_model)
    def put(self, lesson_id, module_id, quiz_id):
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

            quiz = Quiz.query.filter_by(quiz_id=quiz_id, module_id=module_id, deleted_at=None).first()
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

@quiz_ns.route('/<int:lesson_id>/module/<int:module_id>/topic/quizzes/<int:quiz_id>/delete')
class DeleteQuiz(Resource):
    @quiz_ns.doc('delete_quiz', description='Delete a quiz (soft delete).', security='BearerAuth')
    @jwt_required()
    @quiz_ns.marshal_with(success_model, code=200)
    @quiz_ns.response(401, 'Unauthorized: Missing or invalid token', error_model)
    @quiz_ns.response(403, 'Admin access required', error_model)
    @quiz_ns.response(404, 'Lesson, module, topic, or quiz not found', error_model)
    @quiz_ns.response(500, 'Unexpected error', error_model)
    def delete(self, lesson_id, module_id, quiz_id):
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

            quiz = Quiz.query.filter_by(quiz_id=quiz_id, module_id=module_id, deleted_at=None).first()
            if not quiz:
                abort(404, 'Quiz not found')

            quiz.deleted_at = get_current_ist()
            db.session.commit()

            return {'message': 'Quiz deleted successfully'}, 200

        except Exception as e:
            db.session.rollback()
            abort(500, f'An unexpected error occurred: {str(e)}')

@quiz_ns.route('/module/<int:module_id>/topic/<int:topic_id>/quizzes/<int:quiz_id>/questions')
class QuestionsByQuiz(Resource):
    @quiz_ns.doc('get_questions_by_quiz', description='Retrieve all questions for a specific quiz.', security='BearerAuth')
    @jwt_required()
    @quiz_ns.marshal_list_with(question_model, code=200)
    @quiz_ns.response(401, 'Unauthorized: Missing or invalid token', error_model)
    @quiz_ns.response(404, 'Lesson, module, topic, or quiz not found', error_model)
    @quiz_ns.response(500, 'Unexpected error', error_model)
    def get(self, lesson_id, module_id, quiz_id):
        """Retrieve all questions for a specific quiz."""
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

            quiz = Quiz.query.filter_by(quiz_id=quiz_id, module_id=module_id, deleted_at=None).first()
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

@quiz_ns.route('/<int:lesson_id>/module/<int:module_id>/topic/quizzes/<int:quiz_id>/question/create')
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
    def post(self, lesson_id, module_id, quiz_id):
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

            quiz = Quiz.query.filter_by(quiz_id=quiz_id, module_id=module_id, deleted_at=None).first()
            if not quiz:
                abort(404, 'Quiz not found')

            data = quiz_ns.payload
            if not all(k in data for k in ['question_text', 'option1', 'option2', 'option3', 'option4', 'correct_answer']):
                abort(400, 'All question fields are required')

            new_question = Question(
                quiz_id=quiz_id,
                created_by_admin_id=user_id,
                question_text=data['question_text'],
                option1=data['option1'],
                option2=data['option2'],
                option3=data['option3'],
                option4=data['option4'],
                correct_answer=data['correct_answer'],
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

@quiz_ns.route('/<int:lesson_id>/module/<int:module_id>/topic/quizzes/<int:quiz_id>/question/<int:question_id>/update')
class UpdateQuestion(Resource):
    @quiz_ns.doc('update_question', description='Update a question.', security='BearerAuth')
    @jwt_required()
    @quiz_ns.expect(update_question_model)
    @quiz_ns.marshal_with(question_model, code=200)
    @quiz_ns.response(400, 'Invalid input', error_model)
    @quiz_ns.response(401, 'Unauthorized: Missing or invalid token', error_model)
    @quiz_ns.response(403, 'Admin access required', error_model)
    @quiz_ns.response(404, 'Lesson, module, topic, or question not found', error_model)
    @quiz_ns.response(500, 'Unexpected error', error_model)
    def put(self, lesson_id, module_id, quiz_id, question_id):
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

            quiz = Quiz.query.filter_by(quiz_id=quiz_id, module_id=module_id, deleted_at=None).first()
            if not quiz:
                abort(404, 'Quiz not found')

            question = Question.query.filter_by(question_id=question_id, quiz_id=quiz_id, deleted_at=None).first()
            if not question:
                abort(404, 'Question not found')

            data = quiz_ns.payload
            print("Updating question with data:", data)
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
                question.correct_answer = data['correct_answer']

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

@quiz_ns.route('/<int:lesson_id>/module/<int:module_id>/topic/quizzes/<int:quiz_id>/question/<int:question_id>/delete')
class DeleteQuestion(Resource):
    @quiz_ns.doc('delete_question', description='Delete a question (soft delete).', security='BearerAuth')
    @jwt_required()
    @quiz_ns.marshal_with(success_model, code=200)
    @quiz_ns.response(401, 'Unauthorized: Missing or invalid token', error_model)
    @quiz_ns.response(403, 'Admin access required', error_model)
    @quiz_ns.response(404, 'Lesson, module, topic, or question not found', error_model)
    @quiz_ns.response(500, 'Unexpected error', error_model)
    def delete(self, lesson_id, module_id, quiz_id, question_id):
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

            quiz = Quiz.query.filter_by(quiz_id=quiz_id, module_id=module_id, deleted_at=None).first()
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