from flask import Blueprint
from flask_restx import Namespace, Resource, fields, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from model import db, User, UserProfile, UserSession
from api_utils import get_current_ist
from werkzeug.security import generate_password_hash
from datetime import datetime

# Define the profile namespace
profile_ns = Namespace('profile', description='User profile operations')

# Define request/response models
profile_model = profile_ns.model('Profile', {
    'user_id': fields.Integer(description='User ID'),
    'email': fields.String(description='User email'),
    'username': fields.String(description='Username'),
    'full_name': fields.String(description='Full name of the user'),
    'gender': fields.String(description='User gender', enum=['male', 'female', 'other']),
    'birth_date': fields.String(description='Birth date in YYYY-MM-DD format'),
    'parent_email': fields.String(description='Parent email address', allow_null=True),
    'is_premium_user': fields.Boolean(description='Premium user status'),
    'created_at': fields.DateTime(description='Date of joining')
})

update_profile_model = profile_ns.model('UpdateProfile', {
    'full_name': fields.String(description='Full name of the user'),
    'gender': fields.String(description='User gender', enum=['male', 'female', 'other']),
    'birth_date': fields.String(description='Birth date in YYYY-MM-DD format'),
})

parent_email_model = profile_ns.model('ParentEmail', {
    'parent_email': fields.String(required=True, description='Parent email address'),
    'parent_password': fields.String(required=True, description='Parent account password')
})

success_model = profile_ns.model('Success', {
    'message': fields.String(description='Success message')
})

error_model = profile_ns.model('Error', {
    'error': fields.String(description='Error message')
})

@profile_ns.route('/get_user_profile')
class Profile(Resource):
    @profile_ns.doc('get_user_profile', description='Retrieve user profile details.', security='BearerAuth')
    @jwt_required()
    @profile_ns.marshal_with(profile_model, code=200)
    @profile_ns.response(401, 'Unauthorized: Missing or invalid token', error_model)
    @profile_ns.response(404, 'User or profile not found', error_model)
    @profile_ns.response(500, 'Unexpected error', error_model)
    def get(self):
        """Retrieve user profile details."""
        try:
            user_id = get_jwt_identity()
            user = User.query.filter_by(user_id=user_id).first()
            if not user:
                abort(404, 'User not found')

            user_profile = UserProfile.query.filter_by(user_id=user_id).first()
            if not user_profile:
                abort(404, 'User profile not found')

            return {
                'user_id': user.user_id,
                'email': user.email,
                'username': user.username,
                'full_name': user_profile.full_name,
                'gender': user_profile.gender,
                'birth_date': user_profile.birth_date.strftime('%Y-%m-%d') if user_profile.birth_date else None,
                'parent_email': user_profile.parent_email,
                'is_premium_user': user_profile.is_premium_user,
                'created_at': user.created_at
            }, 200

        except Exception as e:
            abort(500, f'An unexpected error occurred: {str(e)}')

    @profile_ns.doc('update_user_profile', description='Update user profile details.', security='BearerAuth')
    @jwt_required()
    @profile_ns.expect(update_profile_model)
    @profile_ns.marshal_with(profile_model, code=200)
    @profile_ns.response(400, 'Invalid input', error_model)
    @profile_ns.response(401, 'Unauthorized: Missing or invalid token', error_model)
    @profile_ns.response(404, 'User or profile not found', error_model)
    @profile_ns.response(422, 'Invalid birth_date format or age restriction', error_model)
    @profile_ns.response(500, 'Unexpected error', error_model)
    def put(self):
        """Update user profile details."""
        try:
            user_id = get_jwt_identity()
            user = User.query.filter_by(user_id=user_id).first()
            if not user:
                abort(404, 'User not found')

            user_profile = UserProfile.query.filter_by(user_id=user_id).first()
            if not user_profile:
                abort(404, 'User profile not found')

            data = profile_ns.payload

            # Update fields if provided
            if 'full_name' in data:
                user_profile.full_name = data['full_name']
            if 'gender' in data and data['gender'] in ['male', 'female', 'other']:
                user_profile.gender = data['gender']
            if 'birth_date' in data:
                try:
                    birth_date = datetime.strptime(data['birth_date'], '%Y-%m-%d').date()
                    user_profile.birth_date = birth_date
                    user_profile.validate_age()
                except ValueError:
                    abort(422, 'Invalid birth_date format, use YYYY-MM-DD')

            user_profile.updated_at = get_current_ist()
            db.session.commit()

            return {
                'user_id': user.user_id,
                'email': user.email,
                'username': user.username,
                'full_name': user_profile.full_name,
                'gender': user_profile.gender,
                'birth_date': user_profile.birth_date.strftime('%Y-%m-%d') if user_profile.birth_date else None,
                'parent_email': user_profile.parent_email,
                'is_premium_user': user_profile.is_premium_user,
                'created_at': user.created_at
            }, 200

        except ValueError as e:
            db.session.rollback()
            abort(422, str(e))
        except Exception as e:
            db.session.rollback()
            abort(500, f'An unexpected error occurred: {str(e)}')

@profile_ns.route('/set_parent_email')
class ParentEmail(Resource):
    @profile_ns.doc('set_parent_email', description='Set parent email for the user.', security='BearerAuth')
    @jwt_required()
    @profile_ns.expect(parent_email_model)
    @profile_ns.marshal_with(success_model, code=200)
    @profile_ns.response(400, 'Invalid input', error_model)
    @profile_ns.response(401, 'Unauthorized: Missing or invalid token', error_model)
    @profile_ns.response(404, 'User or profile not found', error_model)
    @profile_ns.response(409, 'Parent email already set', error_model)
    @profile_ns.response(500, 'Unexpected error', error_model)
    def post(self):
        """Set parent email for the user."""
        try:
            user_id = get_jwt_identity()
            user_profile = UserProfile.query.filter_by(user_id=user_id).first()
            if not user_profile:
                abort(404, 'User profile not found')

            if user_profile.parent_email:
                abort(409, 'Parent email already set')

            data = profile_ns.payload
            if not data.get('parent_email') or not data.get('parent_password'):
                abort(400, 'Parent email and password are required')

            user_profile.parent_email = data['parent_email']
            user_profile.parent_password_hash = generate_password_hash(data['parent_password'])
            user_profile.updated_at = get_current_ist()
            db.session.commit()

            return {'message': 'Parent email set successfully'}, 200

        except Exception as e:
            db.session.rollback()
            abort(500, f'An unexpected error occurred: {str(e)}')

@profile_ns.route('/get_user_premium_status')
class PremiumStatus(Resource):
    @profile_ns.doc('get_user_premium_status', description='Check if user is premium.', security='BearerAuth')
    @jwt_required()
    @profile_ns.marshal_with(profile_model, code=200)
    @profile_ns.response(401, 'Unauthorized: Missing or invalid token', error_model)
    @profile_ns.response(404, 'User or profile not found', error_model)
    @profile_ns.response(500, 'Unexpected error', error_model)
    def get(self):
        """Check if user is premium."""
        try:
            user_id = get_jwt_identity()
            user = User.query.filter_by(user_id=user_id).first()
            if not user:
                abort(404, 'User not found')

            user_profile = UserProfile.query.filter_by(user_id=user_id).first()
            if not user_profile:
                abort(404, 'User profile not found')

            return {
                'user_id': user.user_id,
                'email': user.email,
                'username': user.username,
                'full_name': user_profile.full_name,
                'gender': user_profile.gender,
                'birth_date': user_profile.birth_date.strftime('%Y-%m-%d') if user_profile.birth_date else None,
                'parent_email': user_profile.parent_email,
                'is_premium_user': user_profile.is_premium_user,
                'created_at': user.created_at
            }, 200

        except Exception as e:
            abort(500, f'An unexpected error occurred: {str(e)}')

@profile_ns.route('/get_user_sessions')
class Sessions(Resource):
    @profile_ns.doc('get_user_sessions', description='Retrieve user session history.', security='BearerAuth')
    @jwt_required()
    @profile_ns.marshal_list_with(profile_ns.model('Session', {
        'session_id': fields.Integer(description='Session ID'),
        'login_at': fields.DateTime(description='Login time'),
        'logout_at': fields.DateTime(description='Logout time', allow_null=True),
        'session_duration_seconds': fields.Integer(description='Session duration in seconds', allow_null=True)
    }))
    @profile_ns.response(401, 'Unauthorized: Missing or invalid token', error_model)
    @profile_ns.response(404, 'User not found', error_model)
    @profile_ns.response(500, 'Unexpected error', error_model)
    def get(self):
        """Retrieve user session history."""
        try:
            user_id = get_jwt_identity()
            sessions = UserSession.query.filter_by(user_id=user_id).order_by(UserSession.login_at.desc()).all()
            return [{
                'session_id': session.session_id,
                'login_at': session.login_at,
                'logout_at': session.logout_at,
                'session_duration_seconds': session.session_duration_seconds
            } for session in sessions], 200
        except Exception as e:
            abort(500, f'An unexpected error occurred: {str(e)}')