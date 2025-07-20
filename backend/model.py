from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from api_utils import get_current_ist

# Initialize SQLAlchemy
db = SQLAlchemy()

# User Model
class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False, unique=True, index=True)
    username = db.Column(db.String(100), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    user_role = db.Column(db.String(50), nullable=False, default='user')  # 'user' or 'admin'
    created_at = db.Column(db.DateTime, default=get_current_ist)
    updated_at = db.Column(db.DateTime, default=get_current_ist, onupdate=get_current_ist)

    # Relationships
    profile = db.relationship('UserProfile', backref='user', lazy=True, uselist=False, cascade='all, delete-orphan')
    sessions = db.relationship('UserSession', backref='user', lazy=True, cascade='all, delete-orphan')
    topic_progress = db.relationship('UserModuleProgress', backref='user', lazy=True, cascade='all, delete-orphan')
    quiz_attempts = db.relationship('QuizAttempt', backref='user', lazy=True, cascade='all, delete-orphan')
    question_attempts = db.relationship('QuestionAttempt', backref='user', lazy=True, cascade='all, delete-orphan')
    chatbot_messages = db.relationship('ChatbotMessage', backref='user', lazy=True, cascade='all, delete-orphan')
    transactions = db.relationship('Transaction', backref='user', lazy=True, cascade='all, delete-orphan')
    story_interactions = db.relationship('StoryInteraction', backref='user', lazy=True, cascade='all, delete-orphan')
    
    created_modules = db.relationship('Module', backref='creator', lazy=True)
    created_topics = db.relationship('Topic', backref='creator', lazy=True)
    created_quizzes = db.relationship('Quiz', backref='creator', lazy=True)
    created_questions = db.relationship('Question', backref='creator', lazy=True)
    created_stories = db.relationship('Story', backref='creator', lazy=True)

# User Profile Model
class UserProfile(db.Model):
    __tablename__ = 'user_profiles'

    profile_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, unique=True, index=True)
    full_name = db.Column(db.String(100))
    gender = db.Column(db.String(20))  # e.g., 'male', 'female', 'other'
    birth_date = db.Column(db.Date, nullable=True)  # Made nullable to allow incomplete profiles
    parent_email = db.Column(db.String(255))
    parent_password_hash = db.Column(db.String(255))
    is_premium_user = db.Column(db.Boolean, nullable=False, default=False)
    premium_passcode = db.Column(db.String(255))  # Nullable as not all users need it
    created_at = db.Column(db.DateTime, default=get_current_ist)
    updated_at = db.Column(db.DateTime, default=get_current_ist, onupdate=get_current_ist)

    def validate_age(self):
        """Validate that the user's age is between 8 and 100 years if birth_date is provided."""
        if self.birth_date:
            today = date.today()
            age = today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
            if not (8 <= age <= 100):
                raise ValueError("User age must be between 8 and 100 years.")

# User Session Model
class UserSession(db.Model):
    __tablename__ = 'user_sessions'

    session_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    session_token = db.Column(db.String(255), nullable=False, unique=True)
    login_at = db.Column(db.DateTime, default=get_current_ist)
    logout_at = db.Column(db.DateTime)
    session_duration_seconds = db.Column(db.Integer)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    chatbot_messages = db.relationship('ChatbotMessage', backref='session', lazy=True, cascade='all, delete-orphan')

# Lesson Model
class Lesson(db.Model):
    __tablename__ = 'lessons'

    lesson_id = db.Column(db.Integer, primary_key=True)
    lesson_name = db.Column(db.String(255), nullable=False, unique=True)  # e.g., 'Financial Literacy'
    lesson_description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=get_current_ist)
    updated_at = db.Column(db.DateTime, default=get_current_ist, onupdate=get_current_ist)

    modules = db.relationship('Module', backref='lesson', lazy=True, cascade='all, delete-orphan')

# Module Model
class Module(db.Model):
    __tablename__ = 'modules'

    module_id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.lesson_id', ondelete='CASCADE'), nullable=False, index=True)
    created_by_admin_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='RESTRICT'), nullable=False)
    module_title = db.Column(db.String(255), nullable=False)
    module_description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=get_current_ist)
    updated_at = db.Column(db.DateTime, default=get_current_ist, onupdate=get_current_ist)
    deleted_at = db.Column(db.DateTime)

    quizzes = db.relationship('Quiz', backref='module', lazy=True, cascade='all, delete-orphan')
    topics = db.relationship('Topic', backref='module', lazy=True, cascade='all, delete-orphan')

# Topic Model
class Topic(db.Model):
    __tablename__ = 'topics'

    topic_id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.module_id', ondelete='CASCADE'), nullable=False, index=True)
    created_by_admin_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='RESTRICT'), nullable=False)
    topic_title = db.Column(db.String(255), nullable=False)
    topic_content = db.Column(db.LargeBinary, nullable=True)
    created_at = db.Column(db.DateTime, default=get_current_ist)
    updated_at = db.Column(db.DateTime, default=get_current_ist, onupdate=get_current_ist)
    deleted_at = db.Column(db.DateTime)

    quizzes = db.relationship('Quiz', backref='topic', lazy=True, cascade='all, delete-orphan')
    progress = db.relationship('UserModuleProgress', backref='topic', lazy=True, cascade='all, delete-orphan')

# User Module Progress Model
class UserModuleProgress(db.Model):
    __tablename__ = 'user_module_progress'

    progress_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.module_id', ondelete='CASCADE'), nullable=False, index=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.topic_id', ondelete='CASCADE'), nullable=True, index=True)  
    started_at = db.Column(db.DateTime, default=get_current_ist)
    completed_at = db.Column(db.DateTime)
    last_accessed_at = db.Column(db.DateTime, default=get_current_ist)
    progress_percentage = db.Column(db.Integer, default=0)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'module_id', 'topic_id', name='idx_progress_user_module_topic'),
        db.CheckConstraint('progress_percentage BETWEEN 0 AND 100', name='check_progress_percentage'),
    )

# Quiz Model
class Quiz(db.Model):
    __tablename__ = 'quizzes'

    quiz_id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.module_id', ondelete='CASCADE'))
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.topic_id', ondelete='CASCADE'))
    created_by_admin_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='RESTRICT'), nullable=False)
    quiz_title = db.Column(db.String(255), nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    is_visible = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=get_current_ist)
    updated_at = db.Column(db.DateTime, default=get_current_ist, onupdate=get_current_ist)
    deleted_at = db.Column(db.DateTime)

    questions = db.relationship('Question', backref='quiz', lazy=True, cascade='all, delete-orphan')
    quiz_attempts = db.relationship('QuizAttempt', backref='quiz', lazy=True, cascade='all, delete-orphan')
    
    __table_args__ = (
        db.Index('idx_quiz_module_topic', 'module_id', 'topic_id'),
        db.CheckConstraint('duration_minutes > 0', name='check_duration_positive'),
    )

# Question Model
class Question(db.Model):
    __tablename__ = 'questions'

    question_id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.quiz_id', ondelete='CASCADE'), nullable=False, index=True)
    created_by_admin_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='RESTRICT'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    option1 = db.Column(db.String(255), nullable=False)
    option2 = db.Column(db.String(255), nullable=False)
    option3 = db.Column(db.String(255), nullable=False)
    option4 = db.Column(db.String(255), nullable=False)
    correct_answer = db.Column(db.String(255), nullable=True)
    score_points = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=get_current_ist)
    updated_at = db.Column(db.DateTime, default=get_current_ist, onupdate=get_current_ist)
    deleted_at = db.Column(db.DateTime)

    question_attempts = db.relationship('QuestionAttempt', backref='question', lazy=True, cascade='all, delete-orphan')

# Quiz Attempt Model
class QuizAttempt(db.Model):
    __tablename__ = 'quiz_attempts'

    attempt_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    quiz_attempt_access_token = db.Column(db.String(255))
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.quiz_id', ondelete='SET NULL'), nullable=True, index=True)
    total_questions = db.Column(db.Integer, nullable=False, default=0)
    total_score_possible = db.Column(db.Integer, nullable=False, default=0)
    attempted_questions = db.Column(db.Integer, nullable=False, default=0)
    correct_answers = db.Column(db.Integer, nullable=False, default=0)
    incorrect_answers = db.Column(db.Integer, nullable=False, default=0)
    skipped_questions = db.Column(db.Integer, nullable=False, default=0)
    score_earned = db.Column(db.Float, nullable=False, default=0.0)
    time_taken_seconds = db.Column(db.Integer, nullable=False, default=0)
    started_at = db.Column(db.DateTime, default=get_current_ist)
    completed_at = db.Column(db.DateTime)

    question_attempts = db.relationship('QuestionAttempt', backref='quiz_attempt', lazy=True, cascade='all, delete-orphan')

# Question Attempt Model
class QuestionAttempt(db.Model):
    __tablename__ = 'question_attempts'

    question_attempt_id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('quiz_attempts.attempt_id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.question_id', ondelete='SET NULL'), nullable=True, index=True)
    selected_answer = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)
    attempted_at = db.Column(db.DateTime, default=get_current_ist)

# Chatbot Message Model
class ChatbotMessage(db.Model):
    __tablename__ = 'chatbot_messages'

    chat_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    session_id = db.Column(db.Integer, db.ForeignKey('user_sessions.session_id', ondelete='CASCADE'), nullable=False, index=True)
    message_content = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(50), nullable=False)  # 'user' or 'bot'
    sent_at = db.Column(db.DateTime, default=get_current_ist)

# Transaction Model
class Transaction(db.Model):
    __tablename__ = 'transactions'

    transaction_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    transaction_type = db.Column(db.String(50), nullable=False)  # 'expense' or 'income'
    transaction_date = db.Column(db.Date, nullable=False)
    transaction_name = db.Column(db.Text)
    category = db.Column(db.String(100))  # Specified length for consistency
    amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=get_current_ist)

# Story Model
class Story(db.Model):
    __tablename__ = 'stories'

    story_id = db.Column(db.Integer, primary_key=True)
    created_by_admin_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='RESTRICT'), nullable=False)
    story_title = db.Column(db.String(255), nullable=False)
    story_content = db.Column(db.Text, nullable=False)
    story_type = db.Column(db.String(50), nullable=False)
    is_visible = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=get_current_ist)
    updated_at = db.Column(db.DateTime, default=get_current_ist, onupdate=get_current_ist)
    deleted_at = db.Column(db.DateTime)

    interactions = db.relationship('StoryInteraction', backref='story', lazy=True, cascade='all, delete-orphan')

# Story Interaction Model
class StoryInteraction(db.Model):
    __tablename__ = 'story_interactions'

    interaction_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    story_id = db.Column(db.Integer, db.ForeignKey('stories.story_id', ondelete='CASCADE'), nullable=False, index=True)
    viewed_at = db.Column(db.DateTime, default=get_current_ist)
    is_liked = db.Column(db.Boolean, nullable=False, default=False)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'story_id', name='idx_interactions_user_story'),
    )
