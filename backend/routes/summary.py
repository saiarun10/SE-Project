from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func, cast, Date
from model import db, User, UserSession, QuizAttempt, Quiz
from api_utils import get_current_ist


# Create a new namespace for summary-related endpoints
summary_ns = Namespace('summary', description='Admin summary operations')

# Define the response model for Swagger UI documentation
summary_model = summary_ns.model('AdminDashboardSummary', {
    'total_users': fields.Integer(description='Total number of registered users'),
    'daily_active_users': fields.Integer(description='Number of unique users active today'),
    'avg_session_duration': fields.String(description='Average session duration of all completed sessions in minutes'),
    'avg_quiz_score': fields.String(description='Average quiz score as a percentage'),
    'avg_quiz_time': fields.String(description='Average time taken for quizzes in minutes'),
    'total_quizzes': fields.Integer(description='Total number of available quizzes')
})

@summary_ns.route('/admin_dashboard_summary')
class AdminDashboardSummary(Resource):
    @summary_ns.doc(
        'get_admin_dashboard_summary', 
        description='Retrieves key statistics for the admin dashboard.',
        security='BearerAuth'
    )
    @summary_ns.marshal_with(summary_model)
    @jwt_required()
    def get(self):
        """Retrieve admin dashboard summary statistics"""
        # Ensure the user is an admin
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user or user.user_role != 'admin':
            summary_ns.abort(403, 'Admin access required to view statistics.')

        try:
            # 1. Total Registered Users (role='user')
            total_users = User.query.filter_by(user_role='user').count()

            # 2. Daily Active Users (unique users with a session today)
            today_ist = get_current_ist().date()
            daily_active_users = db.session.query(func.count(func.distinct(UserSession.user_id)))\
                .filter(cast(UserSession.login_at, Date) == today_ist).scalar() or 0

            # 3. Average Session Duration for completed sessions
            avg_duration_sec = db.session.query(func.avg(UserSession.session_duration_seconds))\
                .filter(UserSession.session_duration_seconds.isnot(None)).scalar() or 0
            avg_session_duration = f"{round(avg_duration_sec / 60)} Min" if avg_duration_sec else "0 Min"

            # 4. Average Quiz Score
            # Assuming score_earned is the final percentage score
            avg_score = db.session.query(func.avg(QuizAttempt.score_earned)).scalar() or 0
            avg_quiz_score = f"{round(avg_score, 1)}%"

            # 5. Average Quiz Time
            avg_time_sec = db.session.query(func.avg(QuizAttempt.time_taken_seconds)).scalar() or 0
            avg_quiz_time = f"{round(avg_time_sec / 60)} Min" if avg_time_sec else "0 Min"

            # 6. Total Number of Quizzes (not soft-deleted)
            total_quizzes = Quiz.query.filter_by(deleted_at=None).count()

            return {
                'total_users': total_users,
                'daily_active_users': daily_active_users,
                'avg_session_duration': avg_session_duration,
                'avg_quiz_score': avg_quiz_score,
                'avg_quiz_time': avg_quiz_time,
                'total_quizzes': total_quizzes
            }
        except Exception as e:
            # Log the error in a real application
            print(f"Error fetching summary: {e}")
            summary_ns.abort(500, "An error occurred while fetching summary statistics.")
