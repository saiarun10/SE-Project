from flask import jsonify, make_response
from flask_restx import Namespace, Resource, fields, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func, cast, Date, desc
from datetime import timedelta
from werkzeug.security import check_password_hash
import csv
import io

# Import your models and utility functions
from model import db, User, UserProfile, UserSession, QuizAttempt, Quiz, UserModuleProgress, ChatbotMessage, Topic, Module
from api_utils import get_current_ist

# --- Namespace Definition ---
summary_ns = Namespace('summary', description='Admin and User summary and report operations')


# --- Helper function to generate CSV response ---
def json_to_csv_response(data, report_type):
    """Generates a CSV file response from JSON data."""
    output = io.StringIO()
    writer = csv.writer(output)

    # Write metadata
    writer.writerow([f"Report for: {data.get('username', 'N/A')}"])
    writer.writerow([f"Period: {data.get('period', 'N/A')}"])
    writer.writerow([]) # Spacer

    if report_type == 'analytics' and data.get('quiz_attempts'):
        writer.writerow(['--- Quiz Attempts ---'])
        headers = ['Attempt ID', 'Quiz Title', 'Score (%)', 'Time (sec)', 'Completed At']
        writer.writerow(headers)
        for row in data['quiz_attempts']:
            writer.writerow([row['attempt_id'], row['quiz_title'], row['score_earned_percent'], row['time_taken_seconds'], row['completed_at']])
        writer.writerow([]) # Spacer

    if report_type == 'analytics' and data.get('learning_progress'):
        writer.writerow(['--- Learning Progress ---'])
        headers = ['Topic', 'Module', 'Completed At']
        writer.writerow(headers)
        for row in data['learning_progress']:
            writer.writerow([row['topic_title'], row['module_title'], row['completed_at']])
        writer.writerow([]) # Spacer

    if report_type == 'chatbot' and data.get('chat_history'):
        writer.writerow(['--- Chat History ---'])
        headers = ['Timestamp', 'Sender', 'Message']
        writer.writerow(headers)
        for row in data['chat_history']:
            writer.writerow([row['timestamp'], row['sender'], row['message']])

    output.seek(0)
    
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = f"attachment; filename={report_type}_report_{data.get('period', 'all')}.csv"
    response.headers['Content-Type'] = 'text/csv'
    return response


# --- API Models for Swagger ---
admin_summary_model = summary_ns.model('AdminDashboardSummary', {
    'total_users': fields.Integer(description='Total number of registered users'),
    'daily_active_users': fields.Integer(description='Number of unique users active today'),
    'avg_session_duration': fields.String(description='Average session duration of all completed sessions in minutes'),
    'avg_quiz_score': fields.String(description='Average quiz score as a percentage'),
    'avg_quiz_time': fields.String(description='Average time taken for quizzes in minutes'),
    'total_quizzes': fields.Integer(description='Total number of available quizzes')
})

password_model = summary_ns.model('ParentPassword', {
    'password': fields.String(required=True, description='Parent password for verification')
})


# --- Admin Dashboard API ---
@summary_ns.route('/admin_dashboard_summary')
class AdminDashboardSummary(Resource):
    @summary_ns.doc(
        'get_admin_dashboard_summary',
        description='Retrieves key statistics for the admin dashboard.',
        security='BearerAuth'
    )
    @summary_ns.marshal_with(admin_summary_model)
    @jwt_required()
    def get(self):
        """Retrieve admin dashboard summary statistics"""
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user or user.user_role != 'admin':
            summary_ns.abort(403, 'Admin access required to view statistics.')

        try:
            today_ist = get_current_ist().date()
            total_users = User.query.filter_by(user_role='user').count()
            daily_active_users = db.session.query(func.count(func.distinct(UserSession.user_id)))\
                .filter(cast(UserSession.login_at, Date) == today_ist).scalar() or 0
            avg_duration_sec = db.session.query(func.avg(UserSession.session_duration_seconds))\
                .filter(UserSession.session_duration_seconds.isnot(None)).scalar() or 0
            avg_session_duration = f"{round(avg_duration_sec / 60)} Min" if avg_duration_sec else "0 Min"
            avg_score = db.session.query(func.avg(QuizAttempt.score_earned)).scalar() or 0
            avg_quiz_score = f"{round(avg_score, 1)}%"
            avg_time_sec = db.session.query(func.avg(QuizAttempt.time_taken_seconds)).scalar() or 0
            avg_quiz_time = f"{round(avg_time_sec / 60)} Min" if avg_time_sec else "0 Min"
            total_quizzes = Quiz.query.filter_by(deleted_at=None).count()

            return {
                'total_users': total_users, 'daily_active_users': daily_active_users,
                'avg_session_duration': avg_session_duration, 'avg_quiz_score': avg_quiz_score,
                'avg_quiz_time': avg_quiz_time, 'total_quizzes': total_quizzes
            }
        except Exception as e:
            print(f"Error fetching admin summary: {e}")
            summary_ns.abort(500, "An error occurred while fetching admin summary statistics.")


# --- User Summary and Reports APIs ---

# Request parser for time period filtering
period_parser = reqparse.RequestParser()
period_parser.add_argument('period', type=str, default='30d', choices=('1d', '7d', '30d', 'all'), help='Time period for the report')

def get_time_filter(model_field, period):
    """Helper function to create a time-based filter for report queries."""
    end_date = get_current_ist()
    if period == '1d':
        start_date = end_date - timedelta(days=1)
    elif period == '7d':
        start_date = end_date - timedelta(days=7)
    elif period == '30d':
        start_date = end_date - timedelta(days=30)
    else: # 'all'
        return None
    return model_field.between(start_date, end_date)


@summary_ns.route('/user-summary')
class UserSummary(Resource):
    @summary_ns.doc('get_user_summary', security='BearerAuth')
    @jwt_required()
    def get(self):
        """Fetches a comprehensive summary for the logged-in user."""
        user_id = get_jwt_identity()
        user = User.query.options(db.joinedload(User.profile)).get(user_id)
        if not user or not user.profile:
            return {'message': 'User profile not found'}, 404

        # Quiz Stats
        quiz_stats_query = db.session.query(
            func.count(QuizAttempt.attempt_id),
            func.avg(QuizAttempt.score_earned),
            func.sum(QuizAttempt.time_taken_seconds)
        ).filter(QuizAttempt.user_id == user_id).first()
        quiz_time_sec = quiz_stats_query[2] or 0
        quiz_stats = {
            'attempted': quiz_stats_query[0] or 0,
            'averageScore': round(quiz_stats_query[1] or 0, 1),
            'totalTime': round(quiz_time_sec / 60)
        }

        # Learning Stats
        learning_stats = {
            'modulesCompleted': UserModuleProgress.query.filter_by(user_id=user_id, completed_at=db.not_(None)).distinct(UserModuleProgress.module_id).count(),
            'topicsLearned': UserModuleProgress.query.filter_by(user_id=user_id, completed_at=db.not_(None)).distinct(UserModuleProgress.topic_id).count()
        }
        
        # Session and Overall Stats
        all_user_sessions = UserSession.query.filter_by(user_id=user_id).filter(UserSession.session_duration_seconds.isnot(None)).all()
        total_time_spent_sec = sum(s.session_duration_seconds for s in all_user_sessions)
        login_dates = {s.login_at.date() for s in all_user_sessions}
        daily_average_min = (total_time_spent_sec / len(login_dates) / 60) if login_dates else 0

        # Streak Calculation
        streak = 0
        if login_dates:
            sorted_dates = sorted(list(login_dates), reverse=True)
            today = get_current_ist().date()
            if sorted_dates[0] == today or sorted_dates[0] == today - timedelta(days=1):
                streak = 1
                for i in range(len(sorted_dates) - 1):
                    if sorted_dates[i] - timedelta(days=1) == sorted_dates[i+1]:
                        streak += 1
                    else:
                        break
        
        learning_time_min = round((total_time_spent_sec - quiz_time_sec) / 60)
        recent_sessions = UserSession.query.filter_by(user_id=user_id).order_by(desc(UserSession.login_at)).limit(10).all()

        return {
            'username': user.username,
            'quiz': quiz_stats,
            'learning': {**learning_stats, 'totalTime': max(0, learning_time_min)},
            'overall': {'dailyAverage': round(daily_average_min), 'streak': streak},
            'sessions': [{'session_id': s.session_id, 'login_at': s.login_at.isoformat(), 'logout_at': s.logout_at.isoformat() if s.logout_at else None, 'session_duration_seconds': s.session_duration_seconds} for s in recent_sessions],
            'dailyUsageData': {
                'labels': ['Learning', 'Quizzes'],
                'datasets': [{'data': [max(0, learning_time_min), quiz_stats['totalTime']], 'backgroundColor': ['#34a853', '#4285f4']}]
            },
            'isPremium': user.profile.is_premium_user,
            'hasParentEmail': bool(user.profile.parent_email)
        }

@summary_ns.route('/verify-parent-password')
class ParentPasswordVerification(Resource):
    @summary_ns.doc('verify_parent_password', security='BearerAuth')
    @summary_ns.expect(password_model)
    @jwt_required()
    def post(self):
        """Verifies the parent's password for the logged-in user."""
        user_id = get_jwt_identity()
        user_profile = UserProfile.query.filter_by(user_id=user_id).first()
        password = summary_ns.payload['password']

        if not user_profile or not user_profile.parent_password_hash:
            summary_ns.abort(403, 'Parent password is not set for this account.')
        
        if check_password_hash(user_profile.parent_password_hash, password):
            return jsonify({'verified': True})
        else:
            return jsonify({'verified': False})


@summary_ns.route('/user-reports/<string:report_type>')
@summary_ns.param('report_type', 'The type of report to generate (analytics or chatbot)')
class UserReports(Resource):
    @summary_ns.doc('get_user_report', security='BearerAuth', params={'period': 'Time period (1d, 7d, 30d, all)'})
    @jwt_required()
    def get(self, report_type):
        """Generates and returns a user report as a downloadable CSV file."""
        user_id = get_jwt_identity()
        user = User.query.options(db.joinedload(User.profile)).get(user_id)
        
        # Security Checks
        if not user or not user.profile:
            summary_ns.abort(404, "User not found.")
        if not user.profile.is_premium_user:
            summary_ns.abort(403, "Access denied. This feature is for premium users only.")
        if report_type == 'chatbot' and not user.profile.parent_email:
            summary_ns.abort(403, "Access denied. Chat history report requires a registered parent email.")
        if report_type not in ['analytics', 'chatbot']:
            summary_ns.abort(400, "Invalid report type specified.")

        args = period_parser.parse_args()
        report_data = {'username': user.username, 'period': args['period']}

        if report_type == 'analytics':
            # Fetch quiz attempts
            quiz_query = db.session.query(QuizAttempt).filter(QuizAttempt.user_id == user_id)
            time_filter_quiz = get_time_filter(QuizAttempt.completed_at, args['period'])
            if time_filter_quiz is not None:
                quiz_query = quiz_query.filter(time_filter_quiz)
            
            report_data['quiz_attempts'] = [{
                'attempt_id': a.attempt_id, 'quiz_title': a.quiz.quiz_title if a.quiz else 'N/A',
                'score_earned_percent': a.score_earned, 'time_taken_seconds': a.time_taken_seconds,
                'completed_at': a.completed_at.strftime('%Y-%m-%d %H:%M') if a.completed_at else 'N/A'
            } for a in quiz_query.all()]

            # Fetch learning progress
            progress_query = db.session.query(UserModuleProgress).join(Topic).join(Module).filter(UserModuleProgress.user_id == user_id, UserModuleProgress.completed_at.isnot(None))
            time_filter_prog = get_time_filter(UserModuleProgress.completed_at, args['period'])
            if time_filter_prog is not None:
                progress_query = progress_query.filter(time_filter_prog)
            
            report_data['learning_progress'] = [{
                'topic_title': p.topic.topic_title, 'module_title': p.topic.module.module_title,
                'completed_at': p.completed_at.strftime('%Y-%m-%d %H:%M')
            } for p in progress_query.all()]

        elif report_type == 'chatbot':
            # Fetch chat history
            chat_query = db.session.query(ChatbotMessage).filter(ChatbotMessage.user_id == user_id)
            time_filter_chat = get_time_filter(ChatbotMessage.sent_at, args['period'])
            if time_filter_chat is not None:
                chat_query = chat_query.filter(time_filter_chat)
            
            report_data['chat_history'] = [{
                'timestamp': msg.sent_at.strftime('%Y-%m-%d %H:%M:%S'), 'sender': msg.message_type.capitalize(),
                'message': msg.message_content
            } for msg in chat_query.order_by(ChatbotMessage.sent_at).all()]

        return json_to_csv_response(report_data, report_type)