from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
import pytz

# Initialize SQLAlchemy
db = SQLAlchemy()

def get_current_ist():
    """Returns the current datetime in Asia/Kolkata timezone."""
    return datetime.now(pytz.timezone("Asia/Kolkata"))

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
    parental_controls = db.relationship('ParentalControl', backref='user', lazy=True, uselist=False, cascade='all, delete-orphan')
    sessions = db.relationship('UserSession', backref='user', lazy=True, cascade='all, delete-orphan')
    topic_progress = db.relationship('UserTopicProgress', backref='user', lazy=True, cascade='all, delete-orphan')
    quiz_attempts = db.relationship('QuizAttempt', backref='user', lazy=True, cascade='all, delete-orphan')
    question_attempts = db.relationship('QuestionAttempt', backref='user', lazy=True, cascade='all, delete-orphan')
    chatbot_messages = db.relationship('ChatbotMessage', backref='user', lazy=True, cascade='all, delete-orphan')
    expenses = db.relationship('Expense', backref='user', lazy=True, cascade='all, delete-orphan')
    incomes = db.relationship('Income', backref='user', lazy=True, cascade='all, delete-orphan')
    budgets = db.relationship('Budget', backref='user', lazy=True, cascade='all, delete-orphan')
    financial_goals = db.relationship('FinancialGoal', backref='user', lazy=True, cascade='all, delete-orphan')
    user_badges = db.relationship('UserBadge', backref='user', lazy=True, cascade='all, delete-orphan')
    user_points = db.relationship('UserPoint', backref='user', lazy=True, cascade='all, delete-orphan')
    leaderboard = db.relationship('Leaderboard', backref='user', lazy=True, uselist=False, cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='user', lazy=True, cascade='all, delete-orphan')
    story_interactions = db.relationship('StoryInteraction', backref='user', lazy=True, cascade='all, delete-orphan')
    activity_logs = db.relationship('UserActivityLog', backref='user', lazy=True, cascade='all, delete-orphan')
    created_modules = db.relationship('Module', backref='admin', lazy=True)
    created_topics = db.relationship('Topic', backref='admin', lazy=True)
    created_quizzes = db.relationship('Quiz', backref='admin', lazy=True)
    created_questions = db.relationship('Question', backref='admin', lazy=True)
    created_stories = db.relationship('Story', backref='admin', lazy=True)

# User Profile Model
class UserProfile(db.Model):
    __tablename__ = 'user_profiles'

    profile_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, unique=True, index=True)
    full_name = db.Column(db.String(100))
    phone_number = db.Column(db.String(20))
    birth_date = db.Column(db.Date, nullable=False)
    profile_image_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=get_current_ist)
    updated_at = db.Column(db.DateTime, default=get_current_ist, onupdate=get_current_ist)

    def validate_age(self):
        """Validate that the user's age is between 14 and 20 years."""
        today = date.today()
        age = today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        if not (14 <= age <= 60):
            raise ValueError("User age must be between 14 and 60 years.")

# Parental Control Model
class ParentalControl(db.Model):
    __tablename__ = 'parental_controls'

    parental_control_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, unique=True, index=True)
    parent_email = db.Column(db.String(255), nullable=False)
    access_level = db.Column(db.String(50), nullable=False, default='view_progress')  # 'view_progress', 'view_all', 'restrict_content'
    created_at = db.Column(db.DateTime, default=get_current_ist)
    updated_at = db.Column(db.DateTime, default=get_current_ist, onupdate=get_current_ist)

# User Session Model
class UserSession(db.Model):
    __tablename__ = 'user_sessions'

    session_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    client_ip = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    device_info = db.Column(db.String(255))
    mac_address = db.Column(db.String(17))
    memory_size_gb = db.Column(db.Float)
    cpu_core_count = db.Column(db.Integer)
    login_at = db.Column(db.DateTime, default=get_current_ist)
    logout_at = db.Column(db.DateTime)
    session_duration_seconds = db.Column(db.Integer)

    chatbot_messages = db.relationship('ChatbotMessage', backref='session', lazy=True, cascade='all, delete-orphan')

# Lesson Model
class Lesson(db.Model):
    __tablename__ = 'lessons'

    lesson_id = db.Column(db.Integer, primary_key=True)
    lesson_name = db.Column(db.String(255), nullable=False, unique=True)
    lesson_description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=get_current_ist)
    updated_at = db.Column(db.DateTime, default=get_current_ist, onupdate=get_current_ist)
    deleted_at = db.Column(db.DateTime)

    modules = db.relationship('Module', backref='lesson', lazy=True, cascade='all, delete-orphan')

# Module Model
class Module(db.Model):
    __tablename__ = 'modules'

    module_id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.lesson_id', ondelete='CASCADE'), nullable=False, index=True)
    created_by_admin_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='RESTRICT'), nullable=False, index=True)
    module_title = db.Column(db.String(255), nullable=False)
    module_description = db.Column(db.Text)
    requires_payment = db.Column(db.Boolean, nullable=False, default=False)
    payment_amount = db.Column(db.Float, nullable=False, default=0.00)
    is_visible = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=get_current_ist)
    updated_at = db.Column(db.DateTime, default=get_current_ist, onupdate=get_current_ist)
    deleted_at = db.Column(db.DateTime)

    topics = db.relationship('Topic', backref='module', lazy=True, cascade='all, delete-orphan')

# Topic Model
class Topic(db.Model):
    __tablename__ = 'topics'

    topic_id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.module_id', ondelete='CASCADE'), nullable=False, index=True)
    created_by_admin_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='RESTRICT'), nullable=False, index=True)
    topic_title = db.Column(db.String(255), nullable=False)
    topic_content = db.Column(db.Text, nullable=False)
    topic_order = db.Column(db.Integer, nullable=False)
    requires_payment = db.Column(db.Boolean, nullable=False, default=False)
    payment_amount = db.Column(db.Float, nullable=False, default=0.00)
    is_visible = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=get_current_ist)
    updated_at = db.Column(db.DateTime, default=get_current_ist, onupdate=get_current_ist)
    deleted_at = db.Column(db.DateTime)

    quizzes = db.relationship('Quiz', backref='topic', lazy=True, cascade='all, delete-orphan')
    progress = db.relationship('UserTopicProgress', backref='topic', lazy=True, cascade='all, delete-orphan')

# User Topic Progress Model
class UserTopicProgress(db.Model):
    __tablename__ = 'user_topic_progress'

    progress_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.topic_id', ondelete='CASCADE'), nullable=False, index=True)
    started_at = db.Column(db.DateTime, default=get_current_ist)
    completed_at = db.Column(db.DateTime)
    last_accessed_at = db.Column(db.DateTime, default=get_current_ist)
    progress_percentage = db.Column(db.Integer, default=0)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'topic_id', name='idx_progress_user_topic'),
        db.CheckConstraint('progress_percentage BETWEEN 0 AND 100', name='check_progress_percentage'),
    )

# Quiz Model
class Quiz(db.Model):
    __tablename__ = 'quizzes'

    quiz_id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.topic_id', ondelete='CASCADE'), nullable=False, index=True)
    created_by_admin_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='RESTRICT'), nullable=False, index=True)
    quiz_title = db.Column(db.String(255), nullable=False)
    quiz_description = db.Column(db.Text)
    duration_minutes = db.Column(db.Integer, nullable=False)
    requires_payment = db.Column(db.Boolean, nullable=False, default=False)
    payment_amount = db.Column(db.Float, nullable=False, default=0.00)
    is_visible = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=get_current_ist)
    updated_at = db.Column(db.DateTime, default=get_current_ist, onupdate=get_current_ist)
    deleted_at = db.Column(db.DateTime)

    questions = db.relationship('Question', backref='quiz', lazy=True, cascade='all, delete-orphan')
    quiz_attempts = db.relationship('QuizAttempt', backref='quiz', lazy=True)

# Question Model
class Question(db.Model):
    __tablename__ = 'questions'

    question_id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.quiz_id', ondelete='CASCADE'), nullable=False, index=True)
    created_by_admin_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='RESTRICT'), nullable=False, index=True)
    question_text = db.Column(db.Text, nullable=False)
    option1 = db.Column(db.String(255), nullable=False)
    option2 = db.Column(db.String(255), nullable=False)
    option3 = db.Column(db.String(255), nullable=False)
    option4 = db.Column(db.String(255), nullable=False)
    correct_answer = db.Column(db.String(255), nullable=False)
    score_points = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=get_current_ist)
    updated_at = db.Column(db.DateTime, default=get_current_ist, onupdate=get_current_ist)
    deleted_at = db.Column(db.DateTime)

    question_attempts = db.relationship('QuestionAttempt', backref='question', lazy=True)

# Quiz Attempt Model
class QuizAttempt(db.Model):
    __tablename__ = 'quiz_attempts'

    attempt_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.quiz_id', ondelete='SET NULL'), nullable=True, index=True)
    total_questions = db.Column(db.Integer, nullable=False, default=0)
    total_score_possible = db.Column(db.Integer, nullable=False, default=0)
    attempted_questions = db.Column(db.Integer, nullable=False, default=0)
    correct_answers = db.Column(db.Integer, nullable=False, default=0)
    incorrect_answers = db.Column(db.Integer, nullable=False, default=0)
    skipped_questions = db.Column(db.Integer, nullable=False, default=0)
    score_earned = db.Column(db.Float, nullable=False, default=0.00)
    time_taken_seconds = db.Column(db.Integer, nullable=False, default=0)
    started_at = db.Column(db.DateTime, default=get_current_ist)
    completed_at = db.Column(db.DateTime)
    access_token = db.Column(db.String(255))

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

    message_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    session_id = db.Column(db.Integer, db.ForeignKey('user_sessions.session_id', ondelete='CASCADE'), nullable=False, index=True)
    message_content = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(50), nullable=False)
    sent_at = db.Column(db.DateTime, default=get_current_ist)

# Expense Category Model
class ExpenseCategory(db.Model):
    __tablename__ = 'expense_categories'

    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(100), nullable=False, unique=True)
    category_description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=get_current_ist)
    updated_at = db.Column(db.DateTime, default=get_current_ist, onupdate=get_current_ist)

    expenses = db.relationship('Expense', backref='category', lazy=True)
    budget_allocations = db.relationship('BudgetCategoryAllocation', backref='category', lazy=True)

# Expense Model
class Expense(db.Model):
    __tablename__ = 'expenses'

    expense_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('expense_categories.category_id', ondelete='RESTRICT'), nullable=False, index=True)
    amount = db.Column(db.Float, nullable=False)
    expense_description = db.Column(db.Text)
    transaction_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=get_current_ist)
    updated_at = db.Column(db.DateTime, default=get_current_ist, onupdate=get_current_ist)
    deleted_at = db.Column(db.DateTime)

# Income Model
class Income(db.Model):
    __tablename__ = 'incomes'

    income_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    amount = db.Column(db.Float, nullable=False)
    income_source = db.Column(db.String(255), nullable=False)
    received_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=get_current_ist)
    updated_at = db.Column(db.DateTime, default=get_current_ist, onupdate=get_current_ist)
    deleted_at = db.Column(db.DateTime)

# Budget Model
class Budget(db.Model):
    __tablename__ = 'budgets'

    budget_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    budget_name = db.Column(db.String(100), nullable=False)
    total_income = db.Column(db.Float, nullable=False, default=0.00)
    total_expense_limit = db.Column(db.Float, nullable=False, default=0.00)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=get_current_ist)
    updated_at = db.Column(db.DateTime, default=get_current_ist, onupdate=get_current_ist)
    deleted_at = db.Column(db.DateTime)

    allocations = db.relationship('BudgetCategoryAllocation', backref='budget', lazy=True, cascade='all, delete-orphan')

# Budget Category Allocation Model
class BudgetCategoryAllocation(db.Model):
    __tablename__ = 'budget_category_allocations'

    allocation_id = db.Column(db.Integer, primary_key=True)
    budget_id = db.Column(db.Integer, db.ForeignKey('budgets.budget_id', ondelete='CASCADE'), nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('expense_categories.category_id', ondelete='RESTRICT'), nullable=False, index=True)
    allocated_amount = db.Column(db.Float, nullable=False, default=0.00)
    created_at = db.Column(db.DateTime, default=get_current_ist)
    updated_at = db.Column(db.DateTime, default=get_current_ist, onupdate=get_current_ist)

    __table_args__ = (
        db.UniqueConstraint('budget_id', 'category_id', name='idx_allocations_budget_category'),
    )

# Financial Goal Model
class FinancialGoal(db.Model):
    __tablename__ = 'financial_goals'

    goal_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    goal_name = db.Column(db.String(100), nullable=False)
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, nullable=False, default=0.00)
    deadline_date = db.Column(db.Date)
    status = db.Column(db.String(50), nullable=False, default='active')
    created_at = db.Column(db.DateTime, default=get_current_ist)
    updated_at = db.Column(db.DateTime, default=get_current_ist, onupdate=get_current_ist)
    deleted_at = db.Column(db.DateTime)

# Badge Model
class Badge(db.Model):
    __tablename__ = 'badges'

    badge_id = db.Column(db.Integer, primary_key=True)
    badge_name = db.Column(db.String(100), nullable=False, unique=True)
    badge_description = db.Column(db.Text)
    icon_url = db.Column(db.String(255))
    points_required = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=get_current_ist)
    updated_at = db.Column(db.DateTime, default=get_current_ist, onupdate=get_current_ist)

    user_badges = db.relationship('UserBadge', backref='badge', lazy=True, cascade='all, delete-orphan')

# User Badge Model
class UserBadge(db.Model):
    __tablename__ = 'user_badges'

    user_badge_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    badge_id = db.Column(db.Integer, db.ForeignKey('badges.badge_id', ondelete='CASCADE'), nullable=False, index=True)
    earned_at = db.Column(db.DateTime, default=get_current_ist)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'badge_id', name='idx_user_badges_user_badge'),
    )

# User Point Model
class UserPoint(db.Model):
    __tablename__ = 'user_points'

    point_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    points_earned = db.Column(db.Integer, nullable=False)
    source_type = db.Column(db.String(50), nullable=False)
    source_id = db.Column(db.Integer)
    earned_at = db.Column(db.DateTime, default=get_current_ist)

# Leaderboard Model
class Leaderboard(db.Model):
    __tablename__ = 'leaderboards'

    leaderboard_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, unique=True, index=True)
    total_points = db.Column(db.Integer, nullable=False, default=0)
    rank_position = db.Column(db.Integer, nullable=False)
    updated_at = db.Column(db.DateTime, default=get_current_ist, onupdate=get_current_ist)

# Notification Model
class Notification(db.Model):
    __tablename__ = 'notifications'

    notification_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    notification_type = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=get_current_ist)
    expires_at = db.Column(db.DateTime)

# Story Model
class Story(db.Model):
    __tablename__ = 'stories'

    story_id = db.Column(db.Integer, primary_key=True)
    created_by_admin_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='RESTRICT'), nullable=False, index=True)
    story_title = db.Column(db.String(255), nullable=False)
    story_content = db.Column(db.Text, nullable=False)
    story_type = db.Column(db.String(50), nullable=False)
    requires_payment = db.Column(db.Boolean, nullable=False, default=False)
    payment_amount = db.Column(db.Float, nullable=False, default=0.00)
    is_visible = db.Column(db.Boolean, nullable=False, default=True)
    published_at = db.Column(db.DateTime, default=get_current_ist)
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
    is_liked = db.Column(db.Boolean, default=False)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'story_id', name='idx_interactions_user_story'),
    )

# User Activity Log Model
class UserActivityLog(db.Model):
    __tablename__ = 'user_activity_logs'

    log_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    action_type = db.Column(db.String(50), nullable=False)
    entity_type = db.Column(db.String(50))
    entity_id = db.Column(db.Integer)
    action_details = db.Column(db.Text)
    action_at = db.Column(db.DateTime, default=get_current_ist)