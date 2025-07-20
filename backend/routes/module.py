from flask import Blueprint
from flask_restx import Namespace, Resource, fields, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from model import db, Module, User, Lesson
from api_utils import get_current_ist
from datetime import datetime

# Define the module namespace
module_ns = Namespace('module', description='Module operations  (Learn Module/Admin Module - Teach about the  so many fundamental topics like Stock Market ,Money Management, Budgeting Techniques , Financial Planning and Other Financial Literacy topics.)')

# Define request/response models
module_model = module_ns.model('Module', {
    'module_id': fields.Integer(description='Module ID'),
    'lesson_id': fields.Integer(description='Lesson ID'),
    'created_by_admin_id': fields.Integer(description='Admin ID who created the module'),
    'module_title': fields.String(description='Module title'),
    'module_description': fields.String(description='Module description'),
    'created_at': fields.DateTime(description='Creation date'),
    'updated_at': fields.DateTime(description='Last updated date')
})

create_module_model = module_ns.model('CreateModule', {
    'module_title': fields.String(required=True, description='Module title'),
    'module_description': fields.String(description='Module description')
})

update_module_model = module_ns.model('UpdateModule', {
    'module_title': fields.String(description='Module title'),
    'module_description': fields.String(description='Module description')
})

success_model = module_ns.model('Success', {
    'message': fields.String(description='Success message')
})

error_model = module_ns.model('Error', {
    'error': fields.String(description='Error message')
})

@module_ns.route('/get_all_modules')
class Modules(Resource):
    @module_ns.doc('get_all_modules', description='Retrieve all modules.', security='BearerAuth')
    @jwt_required()
    @module_ns.marshal_list_with(module_model, code=200)
    @module_ns.response(401, 'Unauthorized: Missing or invalid token', error_model)
    @module_ns.response(500, 'Unexpected error', error_model)
    def get(self):
        """Retrieve all modules."""
        try:
            user_id = get_jwt_identity()
            user = User.query.filter_by(user_id=user_id).first()
            if not user:
                abort(404, 'User not found')

            modules = Module.query.filter_by(deleted_at=None).all()
            return [{
                'module_id': module.module_id,
                'lesson_id': module.lesson_id,
                'created_by_admin_id': module.created_by_admin_id,
                'module_title': module.module_title,
                'module_description': module.module_description,
                'created_at': module.created_at,
                'updated_at': module.updated_at
            } for module in modules], 200

        except Exception as e:
            abort(500, f'An unexpected error occurred: {str(e)}')

@module_ns.route('/<int:lesson_id>/modules')
class ModulesByLesson(Resource):
    @module_ns.doc('get_modules_by_lesson', description='Retrieve all modules for a specific lesson.', security='BearerAuth')
    @jwt_required()
    @module_ns.marshal_list_with(module_model, code=200)
    @module_ns.response(401, 'Unauthorized: Missing or invalid token', error_model)
    @module_ns.response(404, 'Lesson not found', error_model)
    @module_ns.response(500, 'Unexpected error', error_model)
    def get(self, lesson_id):
        """Retrieve all modules for a specific lesson."""
        try:
            user_id = get_jwt_identity()
            user = User.query.filter_by(user_id=user_id).first()
            if not user:
                abort(404, 'User not found')

            lesson = Lesson.query.filter_by(lesson_id=lesson_id).first()
            if not lesson:
                abort(404, 'Lesson not found')

            modules = Module.query.filter_by(lesson_id=lesson_id, deleted_at=None).all()
            return [{
                'module_id': module.module_id,
                'lesson_id': module.lesson_id,
                'created_by_admin_id': module.created_by_admin_id,
                'module_title': module.module_title,
                'module_description': module.module_description,
                'created_at': module.created_at,
                'updated_at': module.updated_at
            } for module in modules], 200

        except Exception as e:
            abort(500, f'An unexpected error occurred: {str(e)}')

@module_ns.route('/<int:lesson_id>/module/create')
class CreateModule(Resource):
    @module_ns.doc('create_module', description='Create a new module.', security='BearerAuth')
    @jwt_required()
    @module_ns.expect(create_module_model)
    @module_ns.marshal_with(module_model, code=201)
    @module_ns.response(400, 'Invalid input', error_model)
    @module_ns.response(401, 'Unauthorized: Missing or invalid token', error_model)
    @module_ns.response(403, 'Admin access required', error_model)
    @module_ns.response(404, 'Lesson not found', error_model)
    @module_ns.response(500, 'Unexpected error', error_model)
    def post(self, lesson_id):
        """Create a new module."""
        try:
            user_id = get_jwt_identity()
            user = User.query.filter_by(user_id=user_id).first()
            if not user or user.user_role != 'admin':
                abort(403, 'Admin access required')

            lesson = Lesson.query.filter_by(lesson_id=lesson_id).first()
            if not lesson:
                abort(404, 'Lesson not found')

            data = module_ns.payload
            if not data.get('module_title'):
                abort(400, 'Module title is required')

            new_module = Module(
                lesson_id=lesson_id,
                created_by_admin_id=user_id,
                module_title=data['module_title'],
                module_description=data.get('module_description'),
                created_at=get_current_ist(),
                updated_at=get_current_ist()
            )
            db.session.add(new_module)
            db.session.commit()

            return {
                'module_id': new_module.module_id,
                'lesson_id': new_module.lesson_id,
                'created_by_admin_id': new_module.created_by_admin_id,
                'module_title': new_module.module_title,
                'module_description': new_module.module_description,
                'created_at': new_module.created_at,
                'updated_at': new_module.updated_at
            }, 201

        except Exception as e:
            db.session.rollback()
            abort(500, f'An unexpected error occurred: {str(e)}')

@module_ns.route('/<int:lesson_id>/module/<int:module_id>/update')
class UpdateModule(Resource):
    @module_ns.doc('update_module', description='Update a module.', security='BearerAuth')
    @jwt_required()
    @module_ns.expect(update_module_model)
    @module_ns.marshal_with(module_model, code=200)
    @module_ns.response(401, 'Unauthorized: Missing or invalid token', error_model)
    @module_ns.response(403, 'Admin access required', error_model)
    @module_ns.response(404, 'Lesson or module not found', error_model)
    @module_ns.response(500, 'Unexpected error', error_model)
    def put(self, lesson_id, module_id):
        """Update a module."""
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

            data = module_ns.payload
            if 'module_title' in data:
                module.module_title = data['module_title']
            if 'module_description' in data:
                module.module_description = data['module_description']
            
            module.updated_at = get_current_ist()
            db.session.commit()

            return {
                'module_id': module.module_id,
                'lesson_id': module.lesson_id,
                'created_by_admin_id': module.created_by_admin_id,
                'module_title': module.module_title,
                'module_description': module.module_description,
                'created_at': module.created_at,
                'updated_at': module.updated_at
            }, 200

        except Exception as e:
            db.session.rollback()
            abort(500, f'An unexpected error occurred: {str(e)}')

@module_ns.route('/<int:lesson_id>/module/<int:module_id>/delete')
class DeleteModule(Resource):
    @module_ns.doc('delete_module', description='Delete a module (soft delete).', security='BearerAuth')
    @jwt_required()
    @module_ns.marshal_with(success_model, code=200)
    @module_ns.response(401, 'Unauthorized: Missing or invalid token', error_model)
    @module_ns.response(403, 'Admin access required', error_model)
    @module_ns.response(404, 'Lesson or module not found', error_model)
    @module_ns.response(500, 'Unexpected error', error_model)
    def delete(self, lesson_id, module_id):
        """Delete a module (soft delete)."""
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

            module.deleted_at = get_current_ist()
            db.session.commit()

            return {'message': 'Module deleted successfully'}, 200

        except Exception as e:
            db.session.rollback()
            abort(500, f'An unexpected error occurred: {str(e)}')