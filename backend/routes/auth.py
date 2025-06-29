from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flasgger import swag_from
from model import db, User, UserProfile, UserSession
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from api_utils import get_current_ist
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['POST'])
@swag_from('../swagger/signup.yml')
def signup():
    """Register a new user with email, username, and profile details."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is required'}), 400

        required_fields = ['email', 'username', 'password', 'birth_date', 'gender']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields: ' + ', '.join(set(required_fields) - set(data))}), 400

        # Check for existing user
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 409
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already exists'}), 409

        # Validate birth date format
        try:
            birth_date = datetime.strptime(data['birth_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid birth_date format, use YYYY-MM-DD'}), 422

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
            parent_email=data.get('parent_email', None) # Optional field
        )

        # Validate age
        try:
            user_profile.validate_age()
        except ValueError as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 422

        db.session.add(user_profile)
        db.session.commit()

        return jsonify({
            'message': 'User registered successfully',
            'user_id': user.user_id,
            'email': user.email,
            'username': user.username
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
@swag_from('../swagger/login.yml')
def login():
    """Authenticate user and generate JWT token."""
    try:
        data = request.get_json()
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Username and password are required'}), 400

        user = User.query.filter_by(username=data['username']).first()
        if not user:
            return jsonify({'error': 'Invalid username'}), 401
        if not check_password_hash(user.password_hash, data['password']):
            return jsonify({'error': 'Invalid password'}), 401

        # Fetch user profile
        user_profile = UserProfile.query.filter_by(user_id=user.user_id).first()
        parent_email = user_profile.parent_email if user_profile else None 
        is_premium_user = user_profile.is_premium_user if user_profile else False
        # Generate JWT
        access_token = create_access_token(
            identity= str(user.user_id),
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

        return jsonify({
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
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
@swag_from('../swagger/logout.yml')
def logout():
    """Deactivate user session and log out."""
    try:
        user_id = get_jwt_identity()
        session = UserSession.query.filter_by(
            user_id=user_id,
            is_active=True
        ).first()

        if not session:
            return jsonify({'error': 'No active session found'}), 404

        session.is_active = False
        session.logout_at = get_current_ist()
        session_duration_seconds = (session.logout_at - session.login_at).total_seconds()

        print(f"Session login_at: {session.login_at}")
        print(f"Session logout_at: {session.logout_at}")
        print(f"Session duration seconds: {int(session_duration_seconds)}")

        session.session_duration_seconds = int(session_duration_seconds)
        db.session.commit()

        return jsonify({'message': 'Logout successful'}), 200

    except Exception as e:
        db.session.rollback()
        print(f"Error during logout: {str(e)}")
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500