from app import app
from model import db, User, UserProfile, Lesson, get_current_ist
from werkzeug.security import generate_password_hash
from datetime import date

# Configuration for initial admins
INITIAL_ADMINS = [
    {
        "username": "21f1001520",
        "email": "21f1001520@ds.study.iitm.ac.in",
        "password": "123456",
        "full_name": "Shib Kumar Saraf",
        "birth_date": date(2001, 2, 10),
        "gender": "male"
    },
    # Add more admins here in the future, e.g.:
    # {
    #     "username": "22f2001234",
    #     "email": "22f2001234@ds.study.iitm.ac.in",
    #     "password": "password789",
    #     "full_name": "Jane Doe",
    #     "birth_date": date(1999, 5, 15),
    #     "gender": "female"
    # }
]

# Configuration for default lessons
DEFAULT_LESSONS = [
    {
        "name": "Stock Market",
        "description": "Learn the fundamentals of stock markets, including trading, investments, and market analysis."
    },
    {
        "name": "Personal Finance",
        "description": "Understand budgeting, saving, and managing personal finances effectively."
    },
    {
        "name": "Investment Basics",
        "description": "Explore different investment options like mutual funds, bonds, and real estate."
    }
    # Add more lessons here in the future, e.g.:
    # {
    #     "name": "Cryptocurrency",
    #     "description": "Introduction to cryptocurrencies and blockchain technology."
    # }
]

def add_initial_admins():
    """Add initial admin users and their profiles from INITIAL_ADMINS configuration."""
    for admin_config in INITIAL_ADMINS:
        username = admin_config["username"]
        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            try:
                new_admin = User(
                    username=username,
                    email=admin_config["email"],
                    password_hash=generate_password_hash(admin_config["password"]),
                    user_role='admin',
                )
                db.session.add(new_admin)
                db.session.flush()  # Ensure user_id is available

                admin_profile = UserProfile(
                    user_id=new_admin.user_id,
                    full_name=admin_config["full_name"],
                    birth_date=admin_config["birth_date"],
                    gender=admin_config["gender"],
                  
                )
                admin_profile.validate_age()  # Validate age
                db.session.add(admin_profile)
                db.session.commit()
                print(f"Admin '{username}' created successfully with profile.")
            except ValueError as e:
                db.session.rollback()
                print(f"Failed to create admin '{username}' profile: {e}")
            except Exception as e:
                db.session.rollback()
                print(f"Unexpected error creating admin '{username}': {e}")
        else:
            print(f"Admin '{username}' already exists, skipping creation.")

def add_default_lessons():
    """Add default lessons from DEFAULT_LESSONS configuration."""
    for lesson_config in DEFAULT_LESSONS:
        lesson_name = lesson_config["name"]
        existing_lesson = Lesson.query.filter_by(lesson_name=lesson_name).first()
        if not existing_lesson:
            try:
                new_lesson = Lesson(
                    lesson_name=lesson_name,
                    lesson_description=lesson_config["description"],
                )
                db.session.add(new_lesson)
                db.session.commit()
                print(f"Lesson '{lesson_name}' created successfully.")
            except Exception as e:
                db.session.rollback()
                print(f"Failed to create lesson '{lesson_name}': {e}")
        else:
            print(f"Lesson '{lesson_name}' already exists, skipping creation.")

def setup_database():
    """Set up the database by creating tables and adding initial data."""
    with app.app_context():
        # Create all database tables
        db.create_all()
        print("Database tables created.")

        # Add initial admins
        add_initial_admins()

        # Add default lessons
        add_default_lessons()

        print("Database setup complete.")

if __name__ == "__main__":
    setup_database()