from app import app
from model import db, User, UserProfile
from werkzeug.security import generate_password_hash
from datetime import date

with app.app_context():
    # Create all database tables
    db.create_all()

    # Create an initial admin user
    admin_username = "21f1001520"
    admin_email = "21f1001520@ds.study.iitm.ac.in"
    admin_password = "123456"
    admin_full_name = "Admin One"
    admin_birth_date = date(2005, 6, 1)  # Age 19 as of June 3, 2025

    # Check if the admin already exists to avoid duplicates
    existing_user = User.query.filter_by(username=admin_username).first()
    if not existing_user:
        new_admin = User(
            username=admin_username,
            email=admin_email,
            password_hash=generate_password_hash(admin_password),
            user_role='admin'
        )
        db.session.add(new_admin)
        db.session.flush()  # Ensure user_id is available for UserProfile

        # Create a corresponding UserProfile
        admin_profile = UserProfile(
            user_id=new_admin.user_id,
            full_name=admin_full_name,
            birth_date=admin_birth_date
        )
        try:
            admin_profile.validate_age()  # Validate age
            db.session.add(admin_profile)
            db.session.commit()
            print(f"Admin '{admin_username}' created successfully with profile.")
        except ValueError as e:
            db.session.rollback()
            print(f"Failed to create admin profile: {e}")
    else:
        print(f"Admin '{admin_username}' already exists, skipping creation.")
    print("Database setup complete.")