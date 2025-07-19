import stripe
import os
from flask import request
from flask_restx import Namespace, Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from dotenv import load_dotenv

from model import db, User, UserProfile

# Load environment variables
load_dotenv()

# --- Configuration ---
stripe.api_key = os.getenv('STRIPE_API_SECRET_KEY')
FRONTEND_URL = os.getenv('FRONTEND_URL')
if not stripe.api_key:
    raise ValueError("Stripe API key is not set in environment variables.")

# --- Namespace Definition ---
user_payment_ns = Namespace('payment', description='User payment and status operations')

# Parser for the verification endpoint
verify_parser = reqparse.RequestParser()
verify_parser.add_argument('session_id', type=str, required=True, help='Stripe Checkout Session ID is required')

# --- API Resources ---
@user_payment_ns.route('/payment-create-checkout-session')
class CreateCheckoutSession(Resource):
    @jwt_required()
    def post(self):
        """Creates a Stripe Checkout session and returns its URL and ID."""
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user or not user.profile:
            return {'message': 'User profile not found'}, 404
        
        if user.profile.is_premium_user:
            return {'message': 'You are already a premium member'}, 400

        try:
            checkout_session = stripe.checkout.Session.create(
                mode='payment',
                line_items=[{
                    'price_data': {
                        'currency': 'inr',
                        'product_data': { 'name': 'Richie Premium Membership' },
                        'unit_amount': 100000, # ₹1000 in paise
                    },
                    'quantity': 1,
                }],
                client_reference_id=user.user_id,
                success_url=f'{FRONTEND_URL}/buy-premium?success=true',
                cancel_url=f'{FRONTEND_URL}/buy-premium?canceled=true',
            )
            # IMPORTANT: Return both the URL and the session_id
            return {
                'url': checkout_session.url,
                'session_id': checkout_session.id
            }, 200
        except Exception as e:
            user_payment_ns.abort(500, f'Stripe error: {str(e)}')

# --- NEW: Endpoint to verify payment and update the database ---
@user_payment_ns.route('/verify-payment')
class VerifyPayment(Resource):
    @jwt_required()
    @user_payment_ns.expect(verify_parser)
    def post(self):
        """
        Verifies a Stripe payment session and updates the user's premium status.
        """
        args = verify_parser.parse_args()
        session_id = args['session_id']
        current_user_id = get_jwt_identity()

        try:
            # Retrieve the session from Stripe using the API key
            session = stripe.checkout.Session.retrieve(session_id)

            # SECURITY CHECK: Ensure the session belongs to the logged-in user
            if session.client_reference_id != str(current_user_id):
                return {'message': 'Authorization error. Session does not belong to user.'}, 403

            # Check payment status and update DB
            if session.payment_status == 'paid':
                user = User.query.get(current_user_id)
                if user and user.profile:
                    if not user.profile.is_premium_user:
                        user.profile.is_premium_user = True
                        db.session.commit()
                    return {'message': 'Payment successful and account upgraded!', 'is_premium': True}, 200
                else:
                    return {'message': 'User profile not found.'}, 404
            else:
                return {'message': 'Payment not completed.', 'is_premium': False}, 400

        except Exception as e:
            return {'message': f'An error occurred: {str(e)}'}, 500


@user_payment_ns.route('/user-premium-status')
class UserStatus(Resource):
    @jwt_required()
    def get(self):
        """Gets the premium status of the current user."""
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or not user.profile:
             return {'message': 'User or profile not found'}, 404
        return {'is_premium': user.profile.is_premium_user}, 200