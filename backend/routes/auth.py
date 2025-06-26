from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flasgger import swag_from
from model import db, User, UserProfile, UserSession, get_current_ist
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['POST'])
@swag_from('../swagger/signup.yml')
def signup():
    """Register a new user."""
    data = request.get_json()
    required_fields = ['email', 'username', 'password', 'birth_date', 'gender']
    
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    # Check if user already exists
    if User.query.filter_by(email=data['email']).first() or User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Email or username already exists'}), 400

    try:
        birth_date = datetime.strptime(data['birth_date'], '%Y-%m-%d').date()
        # Create user
        user = User(
            email=data['email'],
            username=data['username'],
            password_hash=generate_password_hash(data['password'], method='pbkdf2:sha256'),
            user_role='user',
            created_at=get_current_ist(),
            updated_at=get_current_ist()
        )
        db.session.add(user)
        db.session.flush()  # Get user_id before committing

        # Create user profile
        user_profile = UserProfile(
            user_id=user.user_id,
            full_name=data.get('full_name'),
            phone_number=data.get('phone_number'),
            birth_date=birth_date,
            gender=data['gender'],
            created_at=get_current_ist(),
            updated_at=get_current_ist()
        )

        # Validate age
        user_profile.validate_age()
        db.session.add(user_profile)
        db.session.commit()

        return jsonify({'message': 'User registered successfully', 'user_id': user.user_id}), 201

    except ValueError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 422
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'An error occurred'}), 400

@auth_bp.route('/login', methods=['POST'])
@swag_from('../swagger/login.yml')
def login():
    """Log in a user and return a JWT."""
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password are required'}), 400

    user = User.query.filter_by(username=data['username']).first()
    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({'error': 'Invalid username or password'}), 401

    # Fetch user profile for parent_email
    user_profile = UserProfile.query.filter_by(user_id=user.user_id).first()
    parent_email = user_profile.parent_email if user_profile else None

    # Create JWT with user details
    access_token = create_access_token(identity=user.user_id, additional_claims={
        'user_id': user.user_id,
        'email': user.email,
        'username': user.username,
        'user_role': user.user_role,
        'parent_email': parent_email
    })

    # Create a new session
    session = UserSession(
        user_id=user.user_id,
        client_ip=request.remote_addr,
        session_token=access_token,
        is_active=True,
        created_at=get_current_ist()
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
            'parent_email': parent_email
        }
    }), 200

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
@swag_from('../swagger/logout.yml')
def logout():
    """Log out a user by deactivating their session."""
    user_id = get_jwt_identity()
    print(f"User ID from JWT: {user_id}")
    session = UserSession.query.filter_by(user_id=user_id, is_active=True).first()
    
    if session:
        session.is_active = False
        session.logout_at = get_current_ist()
        session.session_duration_seconds = int((get_current_ist() - session.created_at).total_seconds())
        db.session.commit()

    return jsonify({'message': 'Logout successful'}), 200