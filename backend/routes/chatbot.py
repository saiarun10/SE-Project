import os
from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func, cast, Date
from datetime import timedelta
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage
from model import db, User, ChatbotMessage, UserSession, UserProfile
from api_utils import get_current_ist

# --- Service Class for LLM Interaction ---

class GroqLangChainService:
    """
    A service class to encapsulate interactions with the Groq API using LangChain.
    """
    def __init__(self, api_key):
        if not api_key:
            raise ValueError("Groq API key is not set.")
        # Using the model specified in your code
        self.chat_model = ChatGroq(temperature=0.7, model_name="llama3-70b-8192", api_key=api_key)

    def get_chat_response(self, chat_history, user_message):
        """
        Generates a chat response using a predefined system prompt and chat history.
        """
        system_prompt_text = (
            "You are a friendly and encouraging financial literacy chatbot for children aged 8-14. "
            "Your name is 'FinBot'. Your goal is to explain financial concepts in a simple, engaging, and easy-to-understand way. "
            "Use analogies and examples that kids can relate to (like saving allowance, video game currency, or trading cards). "
            "Keep your answers concise and positive. If a question is not related to finance, money, saving, investing, or economics, "
            "politely steer the conversation back by saying something like, 'That's an interesting question! But my specialty is money. "
            "Do you have any questions about saving or earning?'"
        )
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_prompt_text),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("{human_input}")
        ])

        chain = prompt | self.chat_model
        
        response = chain.invoke({
            "chat_history": chat_history,
            "human_input": user_message
        })
        
        return response.content

# --- API Initialization ---

# It's recommended to set your API key as an environment variable
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# Initialize the service
try:
    groq_service = GroqLangChainService(api_key=GROQ_API_KEY)
except ValueError as e:
    print(f"Initialization Error: {e}")
    groq_service = None

# --- User-Facing Chatbot API ---

chatbot_ns = Namespace('chatbot', description='AI Driven Modern Chatbot for Financial Literacy - Interact with a friendly AI chatbot to learn about financial concepts, ask questions, and get personalized advice on topics like saving, budgeting, and investing.')

# API Models for user-facing chatbot
chat_request_model = chatbot_ns.model('ChatRequest', {
    'message': fields.String(required=True, description='The user\'s message to the chatbot')
})
message_model = chatbot_ns.model('Message', {
    'sender': fields.String(description="Who sent the message ('user' or 'bot')"),
    'text': fields.String(description='The content of the message'),
    'timestamp': fields.String(description='The time the message was sent')
})
chat_response_model = chatbot_ns.model('ChatResponse', {
    'reply': fields.Nested(message_model, description='The bot\'s reply')
})
chat_history_model = chatbot_ns.model('ChatHistory', {
    'history': fields.List(fields.Nested(message_model), description='The user\'s chat history')
})
# API Model for admin stats - EXPANDED
stats_model = chatbot_ns.model('ChatbotStats', {
    'total_messages': fields.Integer(description='Total number of messages (user and bot).'),
    'total_user_messages': fields.Integer(description='Total number of messages sent by users.'),
    'total_bot_responses': fields.Integer(description='Total number of responses sent by the bot.'),
    'unique_users_chatted': fields.Integer(description='Total number of unique users who have used the chatbot.'),
    'premium_users_chatted': fields.Integer(description='Number of unique premium users who have used the chatbot.'),
    'non_premium_users_chatted': fields.Integer(description='Number of unique non-premium users who have used the chatbot.'),
    'active_users_today': fields.Integer(description='Number of unique users who used the chatbot today.'),
    'active_users_last_7_days': fields.Integer(description='Number of unique users who used the chatbot in the last 7 days.'),
    'avg_messages_per_user': fields.Float(description='Overall average number of messages sent per user.'),
    'avg_messages_per_session': fields.Float(description='Overall average number of messages per chat session.')
})

@chatbot_ns.route('/send_message')
class SendMessage(Resource):
    @chatbot_ns.doc('send_message', security='BearerAuth')
    @chatbot_ns.expect(chat_request_model)
    @chatbot_ns.marshal_with(chat_response_model)
    @jwt_required()
    def post(self):
        """Send a message to the chatbot and get a reply."""
        if not groq_service:
            chatbot_ns.abort(503, "Chatbot service is currently unavailable.")

        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            chatbot_ns.abort(404, "User not found.")

        user_session = UserSession.query.filter_by(user_id=user_id, is_active=True).first()
        if not user_session:
            chatbot_ns.abort(400, "No active session found for the user.")

        if not user.profile or not user.profile.is_premium_user:
            user_message_count = ChatbotMessage.query.filter_by(
                session_id=user_session.session_id,
                message_type='user'
            ).count()
            if user_message_count >= 10:
                chatbot_ns.abort(403, 'You have reached your message limit for this session. Please upgrade to premium for unlimited chats.')

        data = request.get_json()
        user_message_text = data.get('message')
        if not user_message_text:
            chatbot_ns.abort(400, "Message content cannot be empty.")
            
        user_message_db = ChatbotMessage(
            user_id=user_id,
            session_id=user_session.session_id,
            message_content=user_message_text,
            message_type='user',
            sent_at=get_current_ist()
        )
        db.session.add(user_message_db)
        db.session.commit()
        
        try:
            previous_messages_db = ChatbotMessage.query.filter_by(user_id=user_id, session_id=user_session.session_id)\
                                                      .order_by(ChatbotMessage.sent_at.asc()).all()
            
            chat_history_for_langchain = [
                HumanMessage(content=msg.message_content) if msg.message_type == 'user' else AIMessage(content=msg.message_content)
                for msg in previous_messages_db
            ]

            bot_reply_text = groq_service.get_chat_response(chat_history_for_langchain, user_message_text)

            bot_message_db = ChatbotMessage(
                user_id=user_id,
                session_id=user_session.session_id,
                message_content=bot_reply_text,
                message_type='bot',
                sent_at=get_current_ist()
            )
            db.session.add(bot_message_db)
            db.session.commit()
            
            bot_reply = {
                'sender': 'bot',
                'text': bot_reply_text,
                'timestamp': bot_message_db.sent_at.strftime('%I:%M %p')
            }
            return {'reply': bot_reply}
        except Exception as e:
            db.session.rollback()
            print(f"An error occurred while processing the message: {e}")
            chatbot_ns.abort(500, "An error occurred while processing your message.")

@chatbot_ns.route('/chat_history')
class ChatHistory(Resource):
    @chatbot_ns.doc('get_chat_history', security='BearerAuth')
    @chatbot_ns.marshal_with(chat_history_model)
    @jwt_required()
    def get(self):
        """Retrieve the user's chat history for the current session."""
        user_id = get_jwt_identity()
        user_session = UserSession.query.filter_by(user_id=user_id, is_active=True).first()
        if not user_session:
            return {'history': []}

        messages_db = ChatbotMessage.query.filter_by(session_id=user_session.session_id)\
                                          .order_by(ChatbotMessage.sent_at.asc()).all()
        history = [
            {
                'sender': msg.message_type,
                'text': msg.message_content,
                'timestamp': msg.sent_at.strftime('%I:%M %p')
            } for msg in messages_db
        ]
        return {'history': history}
    


@chatbot_ns.route('/chatbot_stats')
class ChatbotStats(Resource):
    @chatbot_ns.doc('get_chatbot_stats', security='BearerAuth')
    @chatbot_ns.marshal_with(stats_model)
    @jwt_required()
    def get(self):
        """Retrieve expanded, overall statistics about chatbot usage."""
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user or user.user_role != 'admin':
            chatbot_ns.abort(403, 'Admin access required to view statistics.')

        try:
            # --- Overall Message Counts ---
            total_messages = db.session.query(func.count(ChatbotMessage.chat_id)).scalar() or 0
            total_user_messages = db.session.query(func.count(ChatbotMessage.chat_id)).filter(ChatbotMessage.message_type == 'user').scalar() or 0
            total_bot_responses = total_messages - total_user_messages
            
            # --- Unique User Counts ---
            unique_users_chatted = db.session.query(func.count(func.distinct(ChatbotMessage.user_id))).scalar() or 0
            
            # --- Premium vs. Non-Premium User Counts ---
            premium_users_chatted = db.session.query(func.count(func.distinct(User.user_id)))\
                .join(UserProfile).join(ChatbotMessage)\
                .filter(UserProfile.is_premium_user == True).scalar() or 0
            
            non_premium_users_chatted = db.session.query(func.count(func.distinct(User.user_id)))\
                .join(UserProfile).join(ChatbotMessage)\
                .filter(UserProfile.is_premium_user == False).scalar() or 0

            # --- User Activity / Frequency ---
            today = get_current_ist().date()
            seven_days_ago = today - timedelta(days=7)
            
            active_users_today = db.session.query(func.count(func.distinct(ChatbotMessage.user_id)))\
                .filter(cast(ChatbotMessage.sent_at, Date) == today).scalar() or 0
            
            active_users_last_7_days = db.session.query(func.count(func.distinct(ChatbotMessage.user_id)))\
                .filter(ChatbotMessage.sent_at >= seven_days_ago).scalar() or 0

            # --- Averages ---
            avg_messages_per_user = 0
            if unique_users_chatted > 0:
                avg_messages_per_user = round(total_user_messages / unique_users_chatted, 2)

            # Subquery to count messages per session
            subquery = db.session.query(
                ChatbotMessage.session_id,
                func.count(ChatbotMessage.chat_id).label('message_count')
            ).group_by(ChatbotMessage.session_id).subquery()
            
            # Average of the counts from the subquery
            avg_messages_per_session_result = db.session.query(func.avg(subquery.c.message_count)).scalar() or 0
            avg_messages_per_session = round(float(avg_messages_per_session_result), 2)


            return {
                'total_messages': total_messages,
                'total_user_messages': total_user_messages,
                'total_bot_responses': total_bot_responses,
                'unique_users_chatted': unique_users_chatted,
                'premium_users_chatted': premium_users_chatted,
                'non_premium_users_chatted': non_premium_users_chatted,
                'active_users_today': active_users_today,
                'active_users_last_7_days': active_users_last_7_days,
                'avg_messages_per_user': avg_messages_per_user,
                'avg_messages_per_session': avg_messages_per_session
            }
        except Exception as e:
            print(f"Error fetching chatbot stats: {e}")
            chatbot_ns.abort(500, "An error occurred while fetching chatbot statistics.")
