from flask import Blueprint, request
from flask_restx import Namespace, Resource, fields, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from model import db, Transaction, User, UserProfile
from api_utils import get_current_ist
from datetime import datetime

# Define the transaction namespace
transaction_ns = Namespace('transaction', description='Transaction operations')
passcode_ns = Namespace('Expense Tracker Passcode', description='Create and verify passcode for expense dashboard')

create_passcode_model = passcode_ns.model('CreatePasscode', {
    'user_id': fields.Integer(description='User ID'),
    'premium_passcode': fields.Integer(description='User passcode')
})

submit_passcode_model = passcode_ns.model('SubmitPasscode', {
    'user_id': fields.Integer(description='User ID'),
    'premium_passcode': fields.Integer(description='User passcode')
})

check_passcode_model = passcode_ns.model('CheckPasscode', {
    'user_id': fields.Integer(description='User ID'),
    'premium_passcode': fields.Integer(description='User passcode')
})

transaction_model = transaction_ns.model('Transaction', {
    'transaction_id': fields.Integer(description='Transaction ID'),
    'user_id': fields.Integer(description='User ID'),
    'transaction_type': fields.String(description='Transaction Type'),
    'transaction_date': fields.Date(description='Transaction Date'),
    'transaction_name': fields.String(description='Transaction Name'),
    'category': fields.String(description='Category'),
    'amount': fields.Float(description='Amount'),
    'created_at': fields.DateTime(description='Creation date'),
})

create_transaction_model = transaction_ns.model('CreateTransaction', {
    'transaction_type': fields.String(description='Transaction Type'),
    'transaction_date': fields.Date(description='Transaction Date'),
    'transaction_name': fields.String(description='Transaction Name'),
    'category': fields.String(description='Category'),
    'amount': fields.Float(description='Amount'),
})

categories_model = transaction_ns.model('Categories', {
    'category': fields.String(description='Transaction category')
})

error_model = transaction_ns.model('Error', {
    'error': fields.String(description='Error message')
})

@passcode_ns.route('/submit_passcode')
class SubmitPasscode(Resource):
    @passcode_ns.doc('Submit Passcode', description='Submit the passcode.', security='BearerAuth')
    @jwt_required()
    @passcode_ns.response(200, 'Success')
    @passcode_ns.response(401, 'Unauthorized', error_model)
    @passcode_ns.response(404, 'User not found', error_model)
    @passcode_ns.response(405, 'No passcode found', error_model)
    @passcode_ns.response(403, 'No passcode entered', error_model)
    @passcode_ns.response(500, 'Unexpected error', error_model)
    def post(self):
        try:
            user_id = get_jwt_identity()
            user = User.query.filter_by(user_id=user_id).first()
            if not user:
                abort(404, 'User not found')

            user_profile = UserProfile.query.filter_by(user_id=user.user_id).first()
            if not user_profile:
                abort(405, "No passcode created")

            user_passcode = user_profile.premium_passcode

            data = request.get_json()
            submitted_passcode = data.get("passcode")
            if not submitted_passcode:
                abort(403, 'No passcode entered')

            return {"success": (user_passcode == submitted_passcode)}, 200

        except Exception as e:
            abort(500, f'An unexpected error occurred: {str(e)}')

@passcode_ns.route('/create_passcode')
class CreatePasscode(Resource):
    @passcode_ns.doc('Create Passcode', description='Create the passcode.', security='BearerAuth')
    @jwt_required()
    @passcode_ns.response(201, 'Passcode created successfully')
    @passcode_ns.response(401, 'Unauthorized', error_model)
    @passcode_ns.response(404, 'User not found', error_model)
    @passcode_ns.response(403, 'No passcode entered', error_model)
    @passcode_ns.response(500, 'Unexpected error', error_model)
    def post(self):
        try:
            user_id = get_jwt_identity()
            user = User.query.filter_by(user_id=user_id).first()
            if not user:
                abort(404, 'User not found')

            user_profile = UserProfile.query.filter_by(user_id=user.user_id).first()
            if not user_profile:
                abort(404, 'User profile not found')

            data = request.get_json()
            new_passcode = data.get("passcode")
            if not new_passcode:
                abort(403, 'No passcode entered')

            user_profile.premium_passcode = new_passcode
            db.session.commit()
            return {"success": True}, 201

        except Exception as e:
            db.session.rollback()
            abort(500, f'An unexpected error occurred: {str(e)}')

@passcode_ns.route('/get_passcode_status')
class CheckPasscode(Resource):
    @passcode_ns.doc('Check Passcode Status', description='Check if a passcode exists.', security='BearerAuth')
    @jwt_required()
    @passcode_ns.response(202, 'Status retrieved')
    @passcode_ns.response(401, 'Unauthorized', error_model)
    @passcode_ns.response(404, 'User not found', error_model)
    @passcode_ns.response(500, 'Unexpected error', error_model)
    def get(self):
        try:
            user_id = get_jwt_identity()
            user = User.query.filter_by(user_id=user_id).first()
            if not user:
                abort(404, 'User not found')

            user_profile = UserProfile.query.filter_by(user_id=user.user_id).first()
            exists = user_profile and user_profile.premium_passcode is not None
            return {"exists": exists}, 202

        except Exception as e:
            abort(500, f'An unexpected error occurred: {str(e)}')

@transaction_ns.route("/get_all_expense")
class Transactions(Resource):
    @transaction_ns.doc('get_all_transactions', description='Retrieve all transactions.', security='BearerAuth')
    @jwt_required()
    @transaction_ns.response(200, 'Success')
    @transaction_ns.response(401, 'Unauthorized', error_model)
    @transaction_ns.response(404, 'User not found', error_model)
    @transaction_ns.response(500, 'Unexpected error', error_model)
    def get(self):
        try:
            user_id = get_jwt_identity()
            user = User.query.filter_by(user_id=user_id).first()
            if not user:
                abort(404, 'User not found')

            transactions = Transaction.query.filter_by(user_id=user.user_id).all()
            return{"expenses": [
                {
                    "date": t.transaction_date.strftime('%Y-%m-%d'),
                    "name": t.transaction_name,
                    "category": t.category,
                    "type": t.transaction_type,
                    "amount": t.amount
                } for t in transactions
            ]}, 200

        except Exception as e:
            abort(500, f'An unexpected error occurred: {str(e)}')

@transaction_ns.route("/get_all_categories")
class Categories(Resource):
    @transaction_ns.doc('get_all_categories', description='Retrieve all transaction categories.', security='BearerAuth')
    @jwt_required()
    @transaction_ns.response(202, 'Success')
    @transaction_ns.response(401, 'Unauthorized', error_model)
    @transaction_ns.response(404, 'User not found', error_model)
    @transaction_ns.response(500, 'Unexpected error', error_model)
    def get(self):
        try:
            user_id = get_jwt_identity()
            user = User.query.filter_by(user_id=user_id).first()
            if not user:
                abort(404, 'User not found')

            transactions = Transaction.query.filter_by(user_id=user.user_id).all()
            categories = list(set(t.category for t in transactions))
            return [{"category": c} for c in categories], 202

        except Exception as e:
            abort(500, f'An unexpected error occurred: {str(e)}')

@transaction_ns.route("/add_expense")
class CreateTransaction(Resource):
    @transaction_ns.doc('add_expense', description='Add a transaction.', security='BearerAuth')
    @jwt_required()
    @transaction_ns.response(201, 'Transaction created successfully')
    @transaction_ns.response(400, 'Missing transaction type', error_model)
    @transaction_ns.response(402, 'Missing transaction details', error_model)
    @transaction_ns.response(401, 'Unauthorized', error_model)
    @transaction_ns.response(404, 'User not found', error_model)
    @transaction_ns.response(500, 'Unexpected error', error_model)
    def post(self):
        try:
            user_id = get_jwt_identity()
            user = User.query.filter_by(user_id=user_id).first()
            if not user:
                abort(404, 'User not found')

            data = request.get_json()
            print(data)
            if not data.get("type"):
                abort(400, "Choose transaction type")
            if not data.get("name"):
                abort(402, "Enter transaction details")

            new_transaction = Transaction(
                transaction_type=data.get("type"),
                transaction_date=datetime.strptime(data.get("date"), '%Y-%m-%d').date(),
                transaction_name=data.get("name"),
                category=data.get("category"),
                amount=float(data.get("amount")),
                user_id=user.user_id,
                created_at=get_current_ist()
            )
            db.session.add(new_transaction)
            db.session.commit()

            return {
                'type': new_transaction.transaction_type,
                'date': new_transaction.transaction_date.strftime('%Y-%m-%d'),
                'name': new_transaction.transaction_name,
                'category': new_transaction.category,
                'amount': new_transaction.amount
            }, 201

        except Exception as e:
            db.session.rollback()
            abort(500, f'An unexpected error occurred: {str(e)}')
