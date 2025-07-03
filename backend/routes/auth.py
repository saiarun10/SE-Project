from flask import Blueprint
from flask_restx import Namespace, Resource, fields, abort
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from model import db, User, UserProfile, UserSession
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from api_utils import get_current_ist
import pytz


# Define the auth namespace
auth_ns = Namespace('auth', description='Authentication operations')

# Define request/response models
signup_model = auth_ns.model('Signup', {
    'email': fields.String(required=True, description='User email address'),
    'username': fields.String(required=True, description='Unique username'),
    'password': fields.String(required=True, description='User password'),
    'birth_date': fields.String(required=True, description='Birth date in YYYY-MM-DD format'),
    'gender': fields.String(required=True, description='User gender', enum=['male', 'female', 'other']),
    'full_name': fields.String(description='Full name of the user'),
    'parent_email': fields.String(description='Parent email address (optional)')
})

user_model = auth_ns.model('User', {
    'user_id': fields.Integer(description='User ID'),
    'email': fields.String(description='User email'),
    'username': fields.String(description='Username'),
    'user_role': fields.String(description='User role'),
    'parent_email': fields.String(description='Parent email', allow_null=True),
    'is_premium_user': fields.Boolean(description='Premium user status')
})

login_model = auth_ns.model('Login', {
    'username': fields.String(required=True, description='Username'),
    'password': fields.String(required=True, description='Password')
})

login_response_model = auth_ns.model('LoginResponse', {
    'message': fields.String(description='Response message'),
    'access_token': fields.String(description='JWT access token'),
    'user': fields.Nested(user_model, description='User details')
})

error_model = auth_ns.model('Error', {
    'error': fields.String(description='Error message')
})

success_model = auth_ns.model('Success', {
    'message': fields.String(description='Success message')
})

# Blueprint for compatibility (optional, can remove if fully using Flask-RESTx)
auth_bp = Blueprint('auth', __name__)

@auth_ns.route('/signup')
class Signup(Resource):
    @auth_ns.doc('signup', description='Register a new user with email, username, and profile details.')
    @auth_ns.expect(signup_model)
    @auth_ns.marshal_with(user_model, code=201)
    @auth_ns.response(400, 'Missing required fields', error_model)
    @auth_ns.response(409, 'Email or username already exists', error_model)
    @auth_ns.response(422, 'Invalid birth_date format or age restriction', error_model)
    @auth_ns.response(500, 'Unexpected error', error_model)
    def post(self):
        """Register a new user."""
        try:
            data = auth_ns.payload
            required_fields = ['email', 'username', 'password', 'birth_date', 'gender']
            if not all(field in data for field in required_fields):
                abort(400, f"Missing required fields: {', '.join(set(required_fields) - set(data))}")

            # Check for existing user
            if User.query.filter_by(email=data['email']).first():
                abort(409, 'Email already exists')
            if User.query.filter_by(username=data['username']).first():
                abort(409, 'Username already exists')

            # Validate birth date format
            try:
                birth_date = datetime.strptime(data['birth_date'], '%Y-%m-%d').date()
            except ValueError:
                abort(422, 'Invalid birth_date format, use YYYY-MM-DD')

            # Create user
            user = User(
                email=data['email'],
                username=data['username'],
                password_hash=generate_password_hash(data['password']),
            )
            db.session.add(user)
            db.session.flush()

            # Create user profile
            user_profile = UserProfile(
                user_id=user.user_id,
                full_name=data.get('full_name'),
                gender=data['gender'],
                birth_date=birth_date,
                parent_email=data.get('parent_email')
            )

            # Validate age
            try:
                user_profile.validate_age()
            except ValueError as e:
                db.session.rollback()
                abort(422, str(e))

            db.session.add(user_profile)
            db.session.commit()

            return {
                'user_id': user.user_id,
                'email': user.email,
                'username': user.username,
                'user_role': user.user_role,
                'parent_email': user_profile.parent_email,
                'is_premium_user': user_profile.is_premium_user
            }, 201

        except Exception as e:
            db.session.rollback()
            abort(500, f'An unexpected error occurred: {str(e)}')

@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.doc('login', description='Authenticate user and generate JWT token.')
    @auth_ns.expect(login_model)
    @auth_ns.marshal_with(login_response_model)
    @auth_ns.response(400, 'Missing username or password', error_model)
    @auth_ns.response(401, 'Invalid username or password', error_model)
    @auth_ns.response(500, 'Unexpected error', error_model)
    def post(self):
        """Authenticate user and generate JWT token."""
        try:
            data = auth_ns.payload
            if not data.get('username') or not data.get('password'):
                abort(400, 'Username and password are required')

            user = User.query.filter_by(username=data['username']).first()
            if not user:
                abort(401, 'Invalid username')
            if not check_password_hash(user.password_hash, data['password']):
                abort(401, 'Invalid password')

            # Fetch user profile
            user_profile = UserProfile.query.filter_by(user_id=user.user_id).first()
            parent_email = user_profile.parent_email if user_profile else None
            is_premium_user = user_profile.is_premium_user if user_profile else False

            # Generate JWT
            access_token = create_access_token(
                identity=str(user.user_id),
                additional_claims={
                    'user_id': user.user_id,
                    'user_email': user.email,
                    'username': user.username,
                    'user_role': user.user_role,
                    'parent_email': parent_email,
                    'is_premium_user': is_premium_user
                }
            )

            # Create session
            session = UserSession(
                user_id=user.user_id,
                session_token=access_token,
                login_at=get_current_ist(),
                is_active=True
            )
            db.session.add(session)
            db.session.commit()

            return {
                'message': 'Login successful',
                'access_token': access_token,
                'user': {
                    'user_id': user.user_id,
                    'email': user.email,
                    'username': user.username,
                    'user_role': user.user_role,
                    'parent_email': parent_email,
                    'is_premium_user': is_premium_user
                }
            }, 200

        except Exception as e:
            db.session.rollback()
            abort(500, f'An unexpected error occurred: {str(e)}')

@auth_ns.route('/logout')
class Logout(Resource):
    @auth_ns.doc('logout', description='Deactivate user session and log out.', security='BearerAuth')
    @jwt_required()
    @auth_ns.marshal_with(success_model, code=200)
    @auth_ns.response(401, 'Unauthorized: Missing or invalid token', error_model)
    @auth_ns.response(404, 'No active session found', error_model)
    @auth_ns.response(500, 'Unexpected error', error_model)
    def post(self):
        """Deactivate user session and log out."""
        try:
            user_id = get_jwt_identity()
            session = UserSession.query.filter_by(
                user_id=user_id,
                is_active=True
            ).first()

            if not session:
                abort(404, 'No active session found')

            session.is_active = False
            session.logout_at = get_current_ist()

            # Ensure both datetimes are timezone-aware
            login_at = session.login_at
            logout_at = session.logout_at
            if login_at.tzinfo is None:
                login_at = login_at.replace(tzinfo=pytz.timezone('Asia/Kolkata'))
            if logout_at.tzinfo is None:
                logout_at = logout_at.replace(tzinfo=pytz.timezone('Asia/Kolkata'))

            session_duration_seconds = (logout_at - login_at).total_seconds()

            print(f"Session login_at: {login_at}")
            print(f"Session logout_at: {logout_at}")
            print(f"Session duration seconds: {int(session_duration_seconds)}")

            session.session_duration_seconds = int(session_duration_seconds)
            db.session.commit()

            return {'message': 'Logout successful'}, 200

        except Exception as e:
            db.session.rollback()
            print(f"Error during logout: {str(e)}")
            abort(500, f'An unexpected error occurred: {str(e)}')

@auth_ns.route('/validate-token')
class ValidateToken(Resource):
    @auth_ns.doc('validate_token', description='Validate JWT token and return user details.', security='BearerAuth')
    @jwt_required()
    @auth_ns.marshal_with(user_model, code=200)
    @auth_ns.response(401, 'Unauthorized: Missing or invalid token', error_model)
    @auth_ns.response(404, 'User not found', error_model)
    @auth_ns.response(500, 'Unexpected error', error_model)
    def get(self):
        """Validate JWT token and return user details."""
        try:
            user_id = get_jwt_identity()
            user = User.query.filter_by(user_id=user_id).first()
            if not user:
                abort(404, 'User not found')

            user_profile = UserProfile.query.filter_by(user_id=user.user_id).first()
            parent_email = user_profile.parent_email if user_profile else None
            is_premium_user = user_profile.is_premium_user if user_profile else False

            return {
                'user_id': user.user_id,
                'email': user.email,
                'username': user.username,
                'user_role': user.user_role,
                'parent_email': parent_email,
                'is_premium_user': is_premium_user
            }, 200

        except Exception as e:
            abort(500, f'An unexpected error occurred: {str(e)}')