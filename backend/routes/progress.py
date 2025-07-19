import traceback
from flask import Blueprint, request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from model import db, UserModuleProgress, User, Module, Topic # Ensure Topic is imported
from api_utils import get_current_ist
from datetime import datetime
from sqlalchemy.exc import IntegrityError # Make sure this is imported

# Define the progress namespace
progress_ns = Namespace('progress', description='User progress tracking operations')

# Define request/response models
progress_request_model = progress_ns.model('ProgressRequest', {
    'user_id': fields.Integer(required=True, description='User ID'),
    'module_id': fields.Integer(required=True, description='Module ID'),
    'topic_id': fields.Integer(required=True, description='Topic ID'),
    'action': fields.String(required=True, description='Action type: started, accessed, completed, paused, resumed, exited, content_loaded',
                            enum=['started', 'accessed', 'completed', 'paused', 'resumed', 'exited', 'content_loaded']), # Added enum for clarity
    'progress_percentage': fields.Integer(description='Progress percentage (0-100)', min=0, max=100)
})

# Full progress response model, including all fields from the UserModuleProgress model
full_progress_response_model = progress_ns.model('FullProgressResponse', {
    'progress_id': fields.Integer(description='Unique ID of the progress record'),
    'user_id': fields.Integer(description='ID of the user'),
    'module_id': fields.Integer(description='ID of the module'),
    'topic_id': fields.Integer(description='ID of the topic'),
    'started_at': fields.DateTime(dt_format='iso8601', description='Timestamp when progress was started (ISO 8601)'),
    'completed_at': fields.DateTime(dt_format='iso8601', description='Timestamp when progress was completed (ISO 8601)'),
    'last_accessed_at': fields.DateTime(dt_format='iso8601', description='Timestamp of last access (ISO 8601)'),
    'progress_percentage': fields.Integer(description='Current progress percentage'),
})

# Specific response model for the POST /user/progress endpoint
post_progress_response_model = progress_ns.model('PostProgressResponse', {
    'message': fields.String(description='Success message'),
    'progress_id': fields.Integer(description='Progress record ID'),
    'progress_percentage': fields.Integer(description='Current progress percentage')
})

# Response model for GET /user/<user_id>/module/<module_id>/progress
module_progress_item_model = progress_ns.model('ModuleProgressItem', {
    'progress_id': fields.Integer(description='Progress record ID'),
    'topic_id': fields.Integer(description='Topic ID'),
    'started_at': fields.DateTime(dt_format='iso8601', description='Timestamp when progress was started (ISO 8601)'),
    'completed_at': fields.DateTime(dt_format='iso8601', description='Timestamp when progress was completed (ISO 8601)'),
    'last_accessed_at': fields.DateTime(dt_format='iso8601', description='Timestamp of last access (ISO 8601)'),
    'progress_percentage': fields.Integer(description='Current progress percentage')
})

module_progress_response_model = progress_ns.model('ModuleProgressResponse', {
    'user_id': fields.Integer(description='User ID'),
    'module_id': fields.Integer(description='Module ID'),
    'progress_records': fields.List(fields.Nested(module_progress_item_model), description='List of progress records for topics in the module')
})


error_model = progress_ns.model('Error', {
    'error': fields.String(description='Error message')
})

@progress_ns.route('/user/progress')
class UserProgressTracking(Resource):
    @progress_ns.doc('track_user_progress', description='Track user progress on topics. This endpoint creates or updates a user\'s progress for a specific topic within a module.', security='BearerAuth')
    @jwt_required()
    @progress_ns.expect(progress_request_model, validate=True) # Added validate=True for automatic validation
    @progress_ns.marshal_with(post_progress_response_model, code=200, description='Progress tracked/updated successfully')
    @progress_ns.response(400, 'Bad request: Missing or invalid data', error_model)
    @progress_ns.response(401, 'Unauthorized: Missing or invalid token, or not authorized to track this user\'s progress', error_model)
    @progress_ns.response(404, 'Not Found: User, module, or topic not found', error_model)
    @progress_ns.response(409, 'Conflict: A progress record for this user, module, and topic may already exist or there is a data conflict.', error_model)
    @progress_ns.response(500, 'Internal Server Error: An unexpected error occurred on the server.', error_model)
    def post(self):
        """Track user progress on a topic."""
        try:
            # Get current user
            current_user_id = int(get_jwt_identity()) # Cast to int immediately
            print(f"DEBUG: Current user ID from JWT: {current_user_id}")
            
            current_user = User.query.filter_by(user_id=current_user_id).first()
            if not current_user:
                print(f"DEBUG: User not found for ID: {current_user_id}")
                return {'error': 'User not found'}, 404

            data = request.get_json()
            print(f"DEBUG: Received data: {data}")
            
            # Validate required fields (Flask-RESTx @expect with validate=True handles this, but good for explicit checks)
            required_fields = ['user_id', 'module_id', 'topic_id', 'action']
            for field in required_fields:
                if field not in data:
                    print(f"DEBUG: Missing required field: {field}")
                    return {'error': f'Missing required field: {field}'}, 400

            user_id_from_request = data['user_id']
            user_id = int(user_id_from_request)
            module_id = data['module_id']
            topic_id = data['topic_id']
            action = data['action']
            
            print(f"DEBUG: Type of current_user_id (from JWT, after cast): {type(current_user_id)}, Value: {current_user_id}")
            print(f"DEBUG: Type of user_id (from request data, after cast): {type(user_id)}, Value: {user_id}")
            print(f"DEBUG: Current User Role: {current_user.user_role}")

            # Verify user can only track their own progress (unless admin)
            if current_user_id != user_id and current_user.user_role != 'admin':
                print(f"DEBUG: UNAUTHORIZED TRIGGERED! Current user ID: {current_user_id}, Requested user ID: {user_id}, Role: {current_user.user_role}")
                return {'error': 'Unauthorized to track progress for this user'}, 401
            else:
                print(f"DEBUG: AUTHORIZATION PASSED! Current user ID: {current_user_id}, Requested user ID: {user_id}, Role: {current_user.user_role}")
                
            # Verify module and topic exist
            module = Module.query.filter_by(module_id=module_id).first()
            if not module:
                print(f"DEBUG: Module not found: {module_id}")
                return {'error': 'Module not found'}, 404
                
            topic = Topic.query.filter_by(topic_id=topic_id).first()
            if not topic:
                print(f"DEBUG: Topic not found: {topic_id}")
                return {'error': 'Topic not found'}, 404

            # Verify module and topic are not soft-deleted if you use deleted_at:
            if hasattr(module, 'deleted_at') and module.deleted_at or \
               hasattr(topic, 'deleted_at') and topic.deleted_at:
                print(f"DEBUG: Module or Topic found but is marked as deleted. Module: {getattr(module, 'deleted_at', 'N/A')}, Topic: {getattr(topic, 'deleted_at', 'N/A')}")
                return {'error': 'Module or Topic not found'}, 404 # Treat as not found if deleted

            print(f"DEBUG: Module and topic found - module: {module.module_title}, topic: {topic.topic_title}")

            current_time = get_current_ist()
            print(f"DEBUG: Current time: {current_time}")

            # Check if progress record already exists
            existing_progress = UserModuleProgress.query.filter_by(
                user_id=user_id,
                module_id=module_id,
                topic_id=topic_id
            ).first()

            # Initialize final_progress_record to be used in the response
            final_progress_record = None
            
            if existing_progress:
                print(f"DEBUG: Updating existing progress record ID: {existing_progress.progress_id}. Action: {action}.")
                print(f"DEBUG: Current progress before update: {existing_progress.progress_percentage}%")
                
                # Update existing progress
                progress_record_to_update = existing_progress
                progress_record_to_update.last_accessed_at = current_time
                
                previous_percentage = progress_record_to_update.progress_percentage
                
                # Update progress based on action
                if action == 'started' and not progress_record_to_update.started_at:
                    progress_record_to_update.started_at = current_time
                    progress_record_to_update.progress_percentage = max(progress_record_to_update.progress_percentage, 25)
                    print(f"DEBUG: Set started_at and progress to 25% for existing record.")
                    
                elif action == 'accessed':
                    progress_record_to_update.progress_percentage = max(progress_record_to_update.progress_percentage, 50)
                    print(f"DEBUG: Updated progress for 'accessed' to at least 50% for existing record.")
                    
                elif action == 'content_loaded':
                    progress_record_to_update.progress_percentage = max(progress_record_to_update.progress_percentage, 75)
                    print(f"DEBUG: Updated progress for 'content_loaded' to at least 75% for existing record.")
                    
                elif action == 'completed':
                    progress_record_to_update.progress_percentage = 100
                    progress_record_to_update.completed_at = current_time
                    print(f"DEBUG: Marked as completed (100%) with completed_at for existing record.")
                
                # Handle additional actions without changing progress percentage
                elif action in ['resumed', 'paused', 'exited']:
                    # For 'resumed', ensure started_at is set if it was previously paused/exited
                    if action == 'resumed' and not progress_record_to_update.started_at:
                        progress_record_to_update.started_at = current_time
                    print(f"DEBUG: Handled '{action}' action for existing record - updated last_accessed_at only.")
                
                # Allow manual override of progress percentage
                if 'progress_percentage' in data:
                    manual_progress = data['progress_percentage']
                    if 0 <= manual_progress <= 100:
                        # Only update if manual_progress is higher or if action is 'completed' (for 100%)
                        if manual_progress > progress_record_to_update.progress_percentage or action == 'completed':
                            progress_record_to_update.progress_percentage = manual_progress
                            print(f"DEBUG: Manual progress override to {manual_progress}% for existing record.")
                
                print(f"DEBUG: Progress updated from {previous_percentage}% to {progress_record_to_update.progress_percentage}% for existing record.")
                final_progress_record = progress_record_to_update # Assign to the final record for response
                                
            else: # No existing record, create a new one
                print(f"DEBUG: No existing record found. Creating new progress record for user {user_id}, module {module_id}, topic {topic_id}.")
                
                initial_progress = 0
                started_at_val = None
                completed_at_val = None

                if action == 'started':
                    initial_progress = 25
                    started_at_val = current_time
                elif action == 'accessed':
                    initial_progress = 50
                    started_at_val = current_time # Assume accessed implies it started
                elif action == 'content_loaded':
                    initial_progress = 75
                    started_at_val = current_time # Assume content_loaded implies it started
                elif action == 'completed':
                    initial_progress = 100
                    started_at_val = current_time
                    completed_at_val = current_time
                elif action == 'resumed': # If no record, and 'resumed', treat as a soft start
                    initial_progress = 10
                    started_at_val = current_time
                elif action in ['paused', 'exited']: # If no record, and paused/exited, just create a minimal entry
                    initial_progress = 0 # Or a very small value, e.g., 5, to indicate presence
                    started_at_val = current_time # Still set started_at as they did interact
                
                # Manual override for new record
                if 'progress_percentage' in data:
                    manual_progress = data['progress_percentage']
                    if 0 <= manual_progress <= 100:
                        initial_progress = manual_progress
                        if manual_progress > 0 and not started_at_val: # If manual progress > 0, assume started
                            started_at_val = current_time
                        if manual_progress == 100: # If manual progress is 100, assume completed
                            completed_at_val = current_time

                print(f"DEBUG: New record initial progress set to {initial_progress}%, started_at: {started_at_val}, completed_at: {completed_at_val}.")

                new_progress_record = UserModuleProgress(
                    user_id=user_id,
                    module_id=module_id,
                    topic_id=topic_id,
                    started_at=started_at_val,
                    completed_at=completed_at_val,
                    last_accessed_at=current_time,
                    progress_percentage=initial_progress
                )
                
                db.session.add(new_progress_record)
                print(f"DEBUG: New progress record object added to session. ID before commit: {new_progress_record.progress_id}")
                final_progress_record = new_progress_record # Assign to the final record for response

            # Commit changes
            print(f"DEBUG: Attempting to commit changes to database...")
            db.session.commit()
            print(f"DEBUG: Database commit successful. Final progress record ID after commit: {final_progress_record.progress_id}")
            
            # After commit, the final_progress_record should have its primary key (progress_id) assigned.
            # No need to re-query if SQLAlchemy is configured correctly.
            if final_progress_record.progress_id is None:
                print(f"DEBUG: CRITICAL WARNING - final_progress_record.progress_id is None after commit. This should not happen.")
                # This indicates a deeper issue, but as a fallback, re-query.
                re_queried_record = UserModuleProgress.query.filter_by(
                    user_id=user_id,
                    module_id=module_id,
                    topic_id=topic_id
                ).first()
                if re_queried_record:
                    final_progress_record = re_queried_record
                    print(f"DEBUG: Successfully re-queried record with ID: {final_progress_record.progress_id}")
                else:
                    return {'error': 'Failed to retrieve progress record after saving. Data might be lost.'}, 500

            response_data = {
                'message': f'Progress {action} tracked successfully',
                'progress_id': final_progress_record.progress_id,
                'progress_percentage': final_progress_record.progress_percentage
            }
            
            print(f"DEBUG: Returning successful response: {response_data}")
            return response_data, 200

        except IntegrityError as e:
            db.session.rollback()
            print(f"DEBUG: IntegrityError (e.g., UniqueConstraint) occurred: {str(e.orig)}")
            import traceback
            print(f"DEBUG: Full traceback (IntegrityError): {traceback.format_exc()}")
            error_message = f'Database integrity error: A record for this user, module, and topic may already exist or there is a data conflict.'
            return {'error': error_message}, 409 # Conflict
        
        except Exception as e:
            db.session.rollback()
            print(f"DEBUG: Unexpected Exception occurred: {str(e)}")
            import traceback
            print(f"DEBUG: Full traceback: {traceback.format_exc()}")
            
            error_message = f'An unexpected server error occurred: {str(e)}'
            if hasattr(e, 'orig') and hasattr(e.orig, 'args'):
                error_message = f'Database error: {str(e.orig.args[0]) if e.orig.args else str(e)}'
            
            return {'error': error_message}, 500

@progress_ns.route('/user/<int:user_id>/module/<int:module_id>/progress')
class UserModuleProgressView(Resource):
    @progress_ns.doc('get_user_module_progress', description='Get user progress for all topics within a specific module for a given user.', security='BearerAuth')
    @jwt_required()
    @progress_ns.response(200, 'Success: Returns a list of progress records for the module.', module_progress_response_model)
    @progress_ns.response(401, 'Unauthorized: Missing or invalid token, or not authorized to view this user\'s progress.', error_model)
    @progress_ns.response(404, 'Not Found: User or module not found, or no progress records exist.', error_model)
    @progress_ns.response(500, 'Internal Server Error: An unexpected error occurred on the server.', error_model)
    def get(self, user_id, module_id):
        """Get user progress for a specific module."""
        try:
            # Get current user
            current_user_id = int(get_jwt_identity()) # Cast to int immediately
            current_user = User.query.filter_by(user_id=current_user_id).first()
            if not current_user:
                return {'error': 'User not found'}, 404

            # Verify user can only view their own progress (unless admin)
            if current_user_id != user_id and current_user.user_role != 'admin':
                return {'error': 'Unauthorized to view progress for this user'}, 401

            # Check if module exists
            module = Module.query.filter_by(module_id=module_id).first()
            if not module:
                return {'error': 'Module not found'}, 404
            
            # Get all progress records for this user and module
            progress_records = UserModuleProgress.query.filter_by(
                user_id=user_id,
                module_id=module_id
            ).all()

            result = []
            for record in progress_records:
                result.append({
                    'progress_id': record.progress_id,
                    'topic_id': record.topic_id,
                    'started_at': record.started_at.isoformat() if record.started_at else None,
                    'completed_at': record.completed_at.isoformat() if record.completed_at else None,
                    'last_accessed_at': record.last_accessed_at.isoformat() if record.last_accessed_at else None,
                    'progress_percentage': record.progress_percentage
                })

            if not result: # If no progress records found, but user and module exist
                 return {'error': 'No progress records found for this user in this module.'}, 404

            return {
                'user_id': user_id,
                'module_id': module_id,
                'progress_records': result
            }, 200

        except Exception as e:
            print(f"DEBUG: Error in get_user_module_progress: {e}")
            import traceback
            print(f"DEBUG: Full traceback: {traceback.format_exc()}")
            return {'error': f'An unexpected server error occurred: {str(e)}'}, 500

# Route for fetching a user's progress for a specific topic (GET)
@progress_ns.route('/user/<int:user_id>/module/<int:module_id>/topic/<int:topic_id>/progress')
class UserTopicProgressView(Resource):
    @progress_ns.doc('get_user_topic_progress', description='Get user progress for a specific topic.', security='BearerAuth')
    @jwt_required()
    @progress_ns.marshal_with(full_progress_response_model, code=200, description='Progress record found')
    @progress_ns.response(401, 'Unauthorized', error_model)
    @progress_ns.response(404, 'Not Found: Progress record not found for this topic, or user/module/topic does not exist.', error_model)
    @progress_ns.response(500, 'Internal server error', error_model)
    def get(self, user_id, module_id, topic_id):
        """Get user progress for a specific topic."""
        try:
            current_user_id = int(get_jwt_identity())
            current_user = User.query.filter_by(user_id=current_user_id).first()
            if not current_user:
                return {'error': 'User not found'}, 404

            # Authorization check
            if current_user_id != user_id and current_user.user_role != 'admin':
                return {'error': 'Unauthorized to view this user\'s progress'}, 401

            # Check if module and topic exist
            module = Module.query.filter_by(module_id=module_id).first()
            if not module:
                return {'error': 'Module not found'}, 404
            
            topic = Topic.query.filter_by(topic_id=topic_id).first()
            if not topic:
                return {'error': 'Topic not found'}, 404

            progress_record = UserModuleProgress.query.filter_by(
                user_id=user_id,
                module_id=module_id,
                topic_id=topic_id
            ).first()

            if not progress_record:
                # If no record, return 404 with a clear message
                return {'error': 'No progress record found for this topic.'}, 404

            # Marshal the progress_record directly to the full_progress_response_model
            return progress_record, 200

        except Exception as e:
            print(f"DEBUG: Error in get_user_topic_progress: {e}")
            import traceback
            print(f"DEBUG: Full traceback: {traceback.format_exc()}")
            return {'error': f'An unexpected server error occurred: {str(e)}'}, 500