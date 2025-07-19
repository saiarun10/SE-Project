import random
from app import app
from model import db, User, Lesson, Module, Topic, Quiz, Question

LESSON_STRUCTURE = {
    "Stock Market": [
        {
            "title": "Introduction to the Stock Market",
            "description": "Learn the fundamentals of stocks and markets.",
            "topics": ["What is a Stock?", "How the Stock Market Works", "Reading Stock Tickers"]
        },
        {
            "title": "Investment Strategies",
            "description": "Explore different approaches to investing.",
            "topics": ["Value Investing", "Growth Investing", "Understanding Diversification"]
        }
    ],
    "Banking Sector": [
        {
            "title": "Fundamentals of Banking",
            "description": "Understand the role and function of banks.",
            "topics": ["Types of Bank Accounts", "How Banks Make Money", "The Role of Central Banks"]
        }
    ],
    "Budget": [
        {
            "title": "Creating a Personal Budget",
            "description": "Master the art of managing your money.",
            "topics": ["Tracking Your Income and Expenses", "The 50/30/20 Rule", "Tools for Budgeting"]
        }
    ],
    "Tax": [
        {
            "title": "Understanding Income Tax",
            "description": "Learn the basics of taxation.",
            "topics": ["Tax Brackets and Slabs", "Common Deductions", "How to File a Return"]
        }
    ]
}

def seed_data():
    """
    A flexible and idempotent script to seed the database.
    It checks for existing data before creating anything, allowing it
    to be run multiple times to "fill in the gaps".
    """
    with app.app_context():
        # --- 1. PRE-REQUISITE CHECKS ---
        print("Starting database seeding process...")
        admin_user = User.query.filter_by(user_role='admin').first()
        if not admin_user:
            print("❌ CRITICAL: No admin user found. Please run initial setup first.")
            return

        print(f"✅ Admin user '{admin_user.username}' found.")

        # --- 2. HIERARCHICAL SEEDING ---
        # The script will now walk through the LESSON_STRUCTURE and create
        # anything that is missing in the database.

        for lesson_name, modules_data in LESSON_STRUCTURE.items():
            # -- GET OR VERIFY LESSON --
            lesson_obj = Lesson.query.filter_by(lesson_name=lesson_name).first()
            if not lesson_obj:
                print(f"⚠️ Lesson '{lesson_name}' not found. Skipping. Please run initial setup.")
                continue
            
            print(f"\nProcessing Lesson: {lesson_name}")

            for module_data in modules_data:
                # -- GET OR CREATE MODULE --
                module_obj = Module.query.filter_by(
                    module_title=module_data['title'],
                    lesson_id=lesson_obj.lesson_id
                ).first()

                if not module_obj:
                    module_obj = Module(
                        lesson_id=lesson_obj.lesson_id,
                        created_by_admin_id=admin_user.user_id,
                        module_title=module_data['title'],
                        module_description=module_data['description']
                    )
                    db.session.add(module_obj)
                    db.session.flush() # Use flush to get the ID for child objects
                    print(f"  ✅ Created Module: {module_obj.module_title}")
                else:
                    print(f"  - Found Module: {module_obj.module_title}")

                for topic_title in module_data['topics']:
                    # -- GET OR CREATE TOPIC --
                    topic_obj = Topic.query.filter_by(
                        topic_title=topic_title,
                        module_id=module_obj.module_id
                    ).first()

                    if not topic_obj:
                        topic_obj = Topic(
                            module_id=module_obj.module_id,
                            created_by_admin_id=admin_user.user_id,
                            topic_title=topic_title,
                            topic_content=None # Content is explicitly NULL
                        )
                        db.session.add(topic_obj)
                        db.session.flush()
                        print(f"    ✅ Created Topic: {topic_obj.topic_title}")
                    else:
                        print(f"    - Found Topic: {topic_obj.topic_title}")

                    # -- GET OR CREATE QUIZ (AND ITS QUESTIONS) --
                    quiz_obj = Quiz.query.filter_by(topic_id=topic_obj.topic_id).first()
                    
                    if not quiz_obj:
                        quiz_obj = Quiz(
                            module_id=module_obj.module_id, # Correctly linking module_id
                            topic_id=topic_obj.topic_id,
                            created_by_admin_id=admin_user.user_id,
                            quiz_title=f"Quiz for {topic_obj.topic_title}",
                            duration_minutes=15,
                            is_visible=True
                        )
                        db.session.add(quiz_obj)
                        db.session.flush()
                        print(f"      ✅ Created Quiz for Topic: {topic_obj.topic_title}")

                        # Create 10 dummy questions for the new quiz
                        for i in range(1, 11):
                            correct_answer_text = f"Dummy Correct Answer for Q{i}"
                            options = [
                                correct_answer_text,
                                f"Dummy Option A for Q{i}",
                                f"Dummy Option B for Q{i}",
                                f"Dummy Option C for Q{i}"
                            ]
                            random.shuffle(options)

                            question = Question(
                                quiz_id=quiz_obj.quiz_id,
                                created_by_admin_id=admin_user.user_id,
                                question_text=f"This is dummy question #{i} for '{topic_obj.topic_title}'. What is the answer?",
                                option1=options[0],
                                option2=options[1],
                                option3=options[2],
                                option4=options[3],
                                correct_answer=correct_answer_text,
                                score_points=5
                            )
                            db.session.add(question)
                        print(f"        ✅ Added 10 dummy questions to the quiz.")
                    else:
                        print(f"      - Found Quiz for Topic: {topic_obj.topic_title}. Skipping creation.")
        
        # --- 3. COMMIT ALL CHANGES ---
        try:
            db.session.commit()
            print("\n\nDatabase seeding complete. All changes have been committed. 🎉")
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ An error occurred during commit. All changes rolled back. Error: {e}")


if __name__ == "__main__":
    seed_data()
