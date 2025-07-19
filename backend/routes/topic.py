from flask import Blueprint, request, send_file
from flask_restx import Namespace, Resource, fields, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from model import db, Topic, User, Module, Lesson
from api_utils import get_current_ist
from datetime import datetime
import magic
import io

# Define the topic namespace
topic_ns = Namespace('topic', description='Topic operations')

# Define request/response models
topic_model = topic_ns.model('Topic', {
    'topic_id': fields.Integer(description='Topic ID'),
    'module_id': fields.Integer(description='Module ID'),
    'created_by_admin_id': fields.Integer(description='Admin ID who created the topic'),
    'topic_title': fields.String(description='Topic title'),
    'has_content': fields.Boolean(description='Indicates if topic has uploaded content'),
    'created_at': fields.DateTime(description='Creation date'),
    'updated_at': fields.DateTime(description='Last updated date')
})

create_topic_model = topic_ns.model('CreateTopic', {
    'topic_title': fields.String(required=True, description='Topic title')
})

update_topic_model = topic_ns.model('UpdateTopic', {
    'topic_title': fields.String(description='Topic title')
})

upload_content_model = topic_ns.model('UploadContent', {
    'content_file': fields.Raw(description='Uploaded PDF file')
})

success_model = topic_ns.model('Success', {
    'message': fields.String(description='Success message')
})

error_model = topic_ns.model('Error', {
    'error': fields.String(description='Error message')
})

@topic_ns.route('/get_all_topics')
class Topics(Resource):
    @topic_ns.doc('get_all_topics', description='Retrieve all topics.', security='BearerAuth')
    @jwt_required()
    @topic_ns.marshal_list_with(topic_model, code=200)
    @topic_ns.response(401, 'Unauthorized: Missing or invalid token', error_model)
    @topic_ns.response(500, 'Unexpected error', error_model)
    def get(self):
        """Retrieve all topics."""
        try:
            user_id = get_jwt_identity()
            user = User.query.filter_by(user_id=user_id).first()
            if not user:
                abort(404, 'User not found')

            topics = Topic.query.filter_by(deleted_at=None).all()
            return [{
                'topic_id': topic.topic_id,
                'module_id': topic.module_id,
                'created_by_admin_id': topic.created_by_admin_id,
                'topic_title': topic.topic_title,
                'has_content': bool(topic.topic_content),
                'created_at': topic.created_at,
                'updated_at': topic.updated_at
            } for topic in topics], 200

        except Exception as e:
            abort(500, f'An unexpected error occurred: {str(e)}')

@topic_ns.route('/<int:lesson_id>/module/<int:module_id>/topics')
class TopicsByLessonAndModule(Resource):
    @topic_ns.doc('get_topics_by_lesson_and_module', description='Retrieve all topics for a specific lesson and module.', security='BearerAuth')
    @jwt_required()
    @topic_ns.marshal_list_with(topic_model, code=200)
    @topic_ns.response(401, 'Unauthorized: Missing or invalid token', error_model)
    @topic_ns.response(404, 'Lesson or module not found', error_model)
    @topic_ns.response(500, 'Unexpected error', error_model)
    def get(self, lesson_id, module_id):
        """Retrieve all topics for a specific lesson and module."""
        try:
            user_id = get_jwt_identity()
            user = User.query.filter_by(user_id=user_id).first()
            if not user:
                abort(404, 'User not found')

            lesson = Lesson.query.filter_by(lesson_id=lesson_id).first()
            if not lesson:
                abort(404, 'Lesson not found')

            module = Module.query.filter_by(module_id=module_id, lesson_id=lesson_id, deleted_at=None).first()
            if not module:
                abort(404, 'Module not found')

            topics = Topic.query.filter_by(module_id=module_id, deleted_at=None).all()
            return [{
                'topic_id': topic.topic_id,
                'module_id': topic.module_id,
                'created_by_admin_id': topic.created_by_admin_id,
                'topic_title': topic.topic_title,
                'has_content': bool(topic.topic_content),
                'created_at': topic.created_at,
                'updated_at': topic.updated_at
            } for topic in topics], 200

        except Exception as e:
            abort(500, f'An unexpected error occurred: {str(e)}')

@topic_ns.route('/lesson/<int:lesson_id>/module/<int:module_id>/topic/<int:topic_id>')
class SpecificTopic(Resource):
    @jwt_required()
    def get(self, lesson_id, module_id, topic_id):
        print(f"DEBUG: Received request - lesson_id: {lesson_id}, module_id: {module_id}, topic_id: {topic_id}")
        
        try:
            topic = Topic.query.filter_by(
                topic_id=topic_id,
                module_id=module_id,
                deleted_at=None
            ).first()
            
            print(f"DEBUG: Topic found: {topic}")
            
            if not topic:
                print("DEBUG: Topic not found")
                abort(404, 'Topic not found')
            
            # Handle binary content (PDF files)
            pdf_available = False
            if topic.topic_content:
                try:
                    # Try to decode as UTF-8 first (text content)
                    topic_content = topic.topic_content.decode('utf-8')
                except UnicodeDecodeError:
                    # If it fails, it's likely a PDF file
                    topic_content = None
                    pdf_available = True
            else:
                topic_content = None
            
            return {
                'topic_id': topic.topic_id,
                'module_id': topic.module_id,
                'topic_title': topic.topic_title,
                'topic_content': topic_content,
                'has_pdf': pdf_available,  # Indicate if PDF is available
            }, 200
            
        except Exception as e:
            print(f"DEBUG: Error occurred: {str(e)}")
            print(f"DEBUG: Error type: {type(e)}")
            import traceback
            traceback.print_exc()
            return {'error': 'Internal server error'}, 500

@topic_ns.route('/lesson/<int:lesson_id>/module/<int:module_id>/topic/<int:topic_id>/pdf')
class TopicPDF(Resource):
    def get(self, lesson_id, module_id, topic_id):
        try:
            # Get token from query parameter or header
            from flask import request
            from flask_jwt_extended import decode_token
            
            token = request.args.get('token') or request.headers.get('Authorization', '').replace('Bearer ', '')
            
            if not token:
                abort(401, 'Token required')
            
            # Verify token manually
            try:
                decode_token(token)
            except:
                abort(401, 'Invalid token')
            
            topic = Topic.query.filter_by(
                topic_id=topic_id,
                module_id=module_id,
                deleted_at=None
            ).first()
            
            if not topic or not topic.topic_content:
                abort(404, 'PDF not found')
            
            # Return the PDF binary data
            from flask import Response
            return Response(
                topic.topic_content,
                mimetype='application/pdf',
                headers={
                    'Content-Disposition': f'inline; filename="{topic.topic_title}.pdf"'
                }
            )
            
        except Exception as e:
            print(f"PDF serve error: {str(e)}")
            return {'error': 'Failed to serve PDF'}, 500

@topic_ns.route('/<int:lesson_id>/module/<int:module_id>/topic/create')
class CreateTopic(Resource):
    @topic_ns.doc('create_topic', description='Create a new topic.', security='BearerAuth')
    @jwt_required()
    @topic_ns.expect(create_topic_model)
    @topic_ns.marshal_with(topic_model, code=201)
    @topic_ns.response(400, 'Invalid input', error_model)
    @topic_ns.response(401, 'Unauthorized: Missing or invalid token', error_model)
    @topic_ns.response(403, 'Admin access required', error_model)
    @topic_ns.response(404, 'Lesson or module not found', error_model)
    @topic_ns.response(500, 'Unexpected error', error_model)
    def post(self, lesson_id, module_id):
        """Create a new topic."""
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

            data = topic_ns.payload
            if not data.get('topic_title'):
                abort(400, 'Topic title is required')

            new_topic = Topic(
                module_id=module_id,
                created_by_admin_id=user_id,
                topic_title=data['topic_title'],
                created_at=get_current_ist(),
                updated_at=get_current_ist()
            )
            db.session.add(new_topic)
            db.session.commit()

            return {
                'topic_id': new_topic.topic_id,
                'module_id': new_topic.module_id,
                'created_by_admin_id': new_topic.created_by_admin_id,
                'topic_title': new_topic.topic_title,
                'has_content': False,
                'created_at': new_topic.created_at,
                'updated_at': new_topic.updated_at
            }, 201

        except Exception as e:
            db.session.rollback()
            abort(500, f'An unexpected error occurred: {str(e)}')

@topic_ns.route('/<int:lesson_id>/module/<int:module_id>/topic/<int:topic_id>/update')
class UpdateTopic(Resource):
    @topic_ns.doc('update_topic', description='Update a topic.', security='BearerAuth')
    @jwt_required()
    @topic_ns.expect(update_topic_model)
    @topic_ns.marshal_with(topic_model, code=200)
    @topic_ns.response(401, 'Unauthorized: Missing or invalid token', error_model)
    @topic_ns.response(403, 'Admin access required', error_model)
    @topic_ns.response(404, 'Lesson, module, or topic not found', error_model)
    @topic_ns.response(500, 'Unexpected error', error_model)
    def put(self, lesson_id, module_id, topic_id):
        """Update a topic."""
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

            data = topic_ns.payload
            if 'topic_title' in data:
                topic.topic_title = data['topic_title']
            
            topic.updated_at = get_current_ist()
            db.session.commit()

            return {
                'topic_id': topic.topic_id,
                'module_id': topic.module_id,
                'created_by_admin_id': topic.created_by_admin_id,
                'topic_title': topic.topic_title,
                'has_content': bool(topic.topic_content),
                'created_at': topic.created_at,
                'updated_at': topic.updated_at
            }, 200

        except Exception as e:
            db.session.rollback()
            abort(500, f'An unexpected error occurred: {str(e)}')

@topic_ns.route('/<int:lesson_id>/module/<int:module_id>/topic/<int:topic_id>/delete')
class DeleteTopic(Resource):
    @topic_ns.doc('delete_topic', description='Delete a topic (soft delete).', security='BearerAuth')
    @jwt_required()
    @topic_ns.marshal_with(success_model, code=200)
    @topic_ns.response(401, 'Unauthorized: Missing or invalid token', error_model)
    @topic_ns.response(403, 'Admin access required', error_model)
    @topic_ns.response(404, 'Lesson, module, or topic not found', error_model)
    @topic_ns.response(500, 'Unexpected error', error_model)
    def delete(self, lesson_id, module_id, topic_id):
        """Delete a topic (soft delete)."""
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

            topic.deleted_at = get_current_ist()
            db.session.commit()

            return {'message': 'Topic deleted successfully'}, 200

        except Exception as e:
            db.session.rollback()
            abort(500, f'An unexpected error occurred: {str(e)}')

@topic_ns.route('/<int:lesson_id>/module/<int:module_id>/topic/<int:topic_id>/upload_content')
class UploadContent(Resource):
    @topic_ns.doc('upload_content', description='Upload PDF content for a topic.', security='BearerAuth')
    @jwt_required()
    @topic_ns.expect(upload_content_model)
    @topic_ns.marshal_with(success_model, code=200)
    @topic_ns.response(400, 'Invalid input or non-PDF file', error_model)
    @topic_ns.response(401, 'Unauthorized: Missing or invalid token', error_model)
    @topic_ns.response(403, 'Admin access required', error_model)
    @topic_ns.response(404, 'Lesson, module, or topic not found', error_model)
    @topic_ns.response(500, 'Unexpected error', error_model)
    def post(self, lesson_id, module_id, topic_id):
        """Upload PDF content for a topic."""
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

            if 'content_file' not in request.files:
                abort(400, 'No file part in the request')

            file = request.files['content_file']
            if file.filename == '':
                abort(400, 'No file selected')

            # Validate file type is PDF
            mime = magic.Magic(mime=True)
            file_mime_type = mime.from_buffer(file.read(2048))
            file.seek(0)  # Reset file pointer after reading
            if file_mime_type != 'application/pdf':
                abort(400, 'Only PDF files are allowed')

            topic.topic_content = file.read()
            topic.updated_at = get_current_ist()
            db.session.commit()

            return {'message': 'PDF content uploaded successfully'}, 200

        except Exception as e:
            db.session.rollback()
            abort(500, f'An unexpected error occurred: {str(e)}')

@topic_ns.route('/<int:lesson_id>/module/<int:module_id>/topic/<int:topic_id>/update_content')
class UpdateContent(Resource):
    @topic_ns.doc('update_content', description='Update PDF content for a topic.', security='BearerAuth')
    @jwt_required()
    @topic_ns.expect(upload_content_model)
    @topic_ns.marshal_with(success_model, code=200)
    @topic_ns.response(400, 'Invalid input or non-PDF file', error_model)
    @topic_ns.response(401, 'Unauthorized: Missing or invalid token', error_model)
    @topic_ns.response(403, 'Admin access required', error_model)
    @topic_ns.response(404, 'Lesson, module, or topic not found', error_model)
    @topic_ns.response(500, 'Unexpected error', error_model)
    def post(self, lesson_id, module_id, topic_id):
        """Update PDF content for a topic."""
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

            if 'content_file' not in request.files:
                abort(400, 'No file part in the request')

            file = request.files['content_file']
            if file.filename == '':
                abort(400, 'No file selected')

            # Validate file type is PDF
            mime = magic.Magic(mime=True)
            file_mime_type = mime.from_buffer(file.read(2048))
            file.seek(0)  # Reset file pointer after reading
            if file_mime_type != 'application/pdf':
                abort(400, 'Only PDF files are allowed')

            topic.topic_content = file.read()
            topic.updated_at = get_current_ist()
            db.session.commit()

            return {'message': 'PDF content updated successfully'}, 200

        except Exception as e:
            db.session.rollback()
            abort(500, f'An unexpected error occurred: {str(e)}')

@topic_ns.route('/<int:lesson_id>/module/<int:module_id>/topic/<int:topic_id>/download_content')
class DownloadContent(Resource):
    @topic_ns.doc('download_content', description='Download PDF content for a topic.', security='BearerAuth')
    @jwt_required()
    @topic_ns.response(200, 'PDF content', None)
    @topic_ns.response(401, 'Unauthorized: Missing or invalid token', error_model)
    @topic_ns.response(404, 'Lesson, module, topic, or content not found', error_model)
    @topic_ns.response(500, 'Unexpected error', error_model)
    def get(self, lesson_id, module_id, topic_id):
        """Download PDF content for a topic."""
        try:
            user_id = get_jwt_identity()
            user = User.query.filter_by(user_id=user_id).first()
            if not user:
                abort(404, 'User not found')

            lesson = Lesson.query.filter_by(lesson_id=lesson_id).first()
            if not lesson:
                abort(404, 'Lesson not found')

            module = Module.query.filter_by(module_id=module_id, lesson_id=lesson_id, deleted_at=None).first()
            if not module:
                abort(404, 'Module not found')

            topic = Topic.query.filter_by(topic_id=topic_id, module_id=module_id, deleted_at=None).first()
            if not topic:
                abort(404, 'Topic not found')

            if not topic.topic_content:
                abort(404, 'No content available for this topic')

            return send_file(
                io.BytesIO(topic.topic_content),
                mimetype='application/pdf',
                as_attachment=False,
                download_name=f'topic_{topic_id}_content.pdf'
            )

        except Exception as e:
            abort(500, f'An unexpected error occurred: {str(e)}')

# --- NEWLY ADDED ENDPOINT ---
@topic_ns.route('/<int:lesson_id>/module/<int:module_id>/topic/<int:topic_id>/delete_content')
class DeleteContent(Resource):
    @topic_ns.doc('delete_content', description='Delete the PDF content for a topic.', security='BearerAuth')
    @jwt_required()
    @topic_ns.marshal_with(success_model, code=200)
    @topic_ns.response(401, 'Unauthorized: Missing or invalid token', error_model)
    @topic_ns.response(403, 'Admin access required', error_model)
    @topic_ns.response(404, 'Lesson, module, or topic not found', error_model)
    @topic_ns.response(500, 'Unexpected error', error_model)
    def delete(self, lesson_id, module_id, topic_id):
        """Delete the PDF content for a topic."""
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
            
            if not topic.topic_content:
                return {'message': 'No content to delete'}, 200

            # Set content to NULL and update timestamp
            topic.topic_content = None
            topic.updated_at = get_current_ist()
            db.session.commit()

            return {'message': 'Content deleted successfully'}, 200

        except Exception as e:
            db.session.rollback()
            abort(500, f'An unexpected error occurred: {str(e)}')