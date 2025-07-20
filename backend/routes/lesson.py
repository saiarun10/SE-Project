from flask import Blueprint
from flask_restx import Namespace, Resource, fields, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from model import db, Lesson, User
from api_utils import get_current_ist

# Define the lesson namespace
lesson_ns = Namespace('lesson', description='Lesson operations (Learn Module/Admin Module - Teach about so many fundamental topics like Stock Market ,Money Management, Budgeting Techniques , Financial Planning and Other Financial Literacy topics.)')

# Define request/response models
lesson_model = lesson_ns.model('Lesson', {
    'lesson_id': fields.Integer(description='Lesson ID'),
    'lesson_name': fields.String(description='Lesson name'),
    'lesson_description': fields.String(description='Lesson description'),
    'created_at': fields.DateTime(description='Creation date'),
    'updated_at': fields.DateTime(description='Last updated date')
})

error_model = lesson_ns.model('Error', {
    'error': fields.String(description='Error message')
})

@lesson_ns.route('/get_all_lessons')
class Lessons(Resource):
    @lesson_ns.doc('get_all_lessons', description='Learn Module - Retrieve all lessons for the authenticated user. Teach about the available lessons like Stock Market ,Money Management, Budgeting Techniques , Financial Planning and Other Financial Literacy topics.', security='BearerAuth')
    @jwt_required()
    @lesson_ns.marshal_list_with(lesson_model, code=200)
    @lesson_ns.response(401, 'Unauthorized: Missing or invalid token', error_model)
    @lesson_ns.response(500, 'Unexpected error', error_model)
    def get(self):
        try:
            user_id = get_jwt_identity()
            user = User.query.filter_by(user_id=user_id).first()
            if not user:
                abort(404, 'User not found')

            lessons = Lesson.query.all()
            return [{
                'lesson_id': lesson.lesson_id,
                'lesson_name': lesson.lesson_name,
                'lesson_description': lesson.lesson_description,
                'created_at': lesson.created_at,
                'updated_at': lesson.updated_at
            } for lesson in lessons], 200

        except Exception as e:
            abort(500, f'An unexpected error occurred: {str(e)}')