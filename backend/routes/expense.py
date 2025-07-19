from flask import Blueprint,request
from flask_restx import Namespace, Resource, fields, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from model import db, Transaction,User,UserProfile
from api_utils import get_current_ist
from datetime import datetime


# Define the transaction namespace
transaction_ns = Namespace('transaction', description='Transaction operations')
passcode_ns=Namespace('Expense Tracker Passcode',description='create and verify passcode for expense dashboard')

create_passcode_model=passcode_ns.model('CreatePasscode',{
    'user_id': fields.Integer(description='User ID'),
    'premium_passcode':fields.Integer(description='User passcode')
})

submit_passcode_model=passcode_ns.model('SubmitPasscode',{
    'user_id': fields.Integer(description='User ID'),
    'premium_passcode':fields.Integer(description='User passcode')
})

check_passcode_model=passcode_ns.model('CheckPasscode',{
    'user_id': fields.Integer(description='User ID'),
    'premium_passcode':fields.Integer(description='User passcode')
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
    'transaction_id': fields.Integer(description='Transaction ID'),
    'transaction_type': fields.String(description='Transaction Type'),
    'transaction_date': fields.Date(description='Transaction Date'),
    'transaction_name': fields.String(description='Transaction Name'),
    'category': fields.String(description='Category'),
    'amount': fields.Float(description='Amount'),
})

categories_model=transaction_ns.model('Categories',{
  'category'  :fields.String(description='Transaction category')
})

error_model = transaction_ns.model('Error', {
    'error': fields.String(description='Error message')
})

@passcode_ns.route('/api/submit_passcode')
class SubmitPasscode(Resource):
    @passcode_ns.doc('Submit Passcode', description='Submit the passcode.', security='BearerAuth')
    @jwt_required()
    @passcode_ns.marshal_list_with(submit_passcode_model, code=200)
    @passcode_ns.response(401, 'Unauthorized: Missing or invalid token', error_model)
    @passcode_ns.response(500, 'Unexpected error', error_model)
    @passcode_ns.response(404, 'User not exist', error_model)
    @passcode_ns.response(405, 'No passcode found', error_model)
    @passcode_ns.response(403, 'No passcode entered', error_model)
    def post(self):
        try:
            user_id = get_jwt_identity()
            user = User.query.filter_by(user_id=user_id).first()
            if not user:
                abort(404, 'User not found')
            user_profile=UserProfile.query.filter_by(user_id=user).first()
            
            try:
                user_passcode=user_profile.premium_passcode
            except:
                abort(405,"No passcode created")

            data=request.get_json()
            submitted_passcode=data.get("passcode")
            if not submitted_passcode:
                abort(403,'no passcode entered')

            return {"success":(user_passcode==submitted_passcode)} 
        
        except Exception as e:
            abort(500, f'An unexpected error occurred: {str(e)}')

        
@passcode_ns.route('/api/create_passcode')
class CreatePasscode(Resource):
    @passcode_ns.doc('Create Passcode', description='Create the passcode.', security='BearerAuth')
    @jwt_required()
    @passcode_ns.marshal_list_with(create_passcode_model, code=201)
    @passcode_ns.response(401, 'Unauthorized: Missing or invalid token', error_model)
    @passcode_ns.response(500, 'Unexpected error', error_model)
    @passcode_ns.response(404, 'User not exist', error_model)
    @passcode_ns.response(403, 'No passcode entered', error_model)
    def post(self):
        try:
            user_id = get_jwt_identity()
            user = User.query.filter_by(user_id=user_id).first()
            if not user:
                abort(404, 'User not found')
            user_profile=UserProfile.query.filter_by(user_id=user).first()

            data=request.get_json()
            new_passcode=data.get("passcode")
            if not new_passcode:
                abort(403,'no passcode entered')
            user_profile.premium_passcode=new_passcode
            db.session.commit()
            return True
        
        except Exception as e:
            abort(500, f'An unexpected error occurred: {str(e)}')

@passcode_ns.route('/api/get_passcode_status')
class CheckPasscode(Resource):
    @passcode_ns.doc('Check Passcode Status', description='Check Passcode Status.', security='BearerAuth')
    @jwt_required()
    @passcode_ns.marshal_list_with(check_passcode_model, code=202)
    @passcode_ns.response(401, 'Unauthorized: Missing or invalid token', error_model)
    @passcode_ns.response(500, 'Unexpected error', error_model)
    @passcode_ns.response(404, 'User not exist', error_model)
    def get(self):
        try:
            user_id = get_jwt_identity()
            user = User.query.filter_by(user_id=user_id).first()
            if not user:
                abort(404, 'User not found')
            user_profile=UserProfile.query.filter_by(user_id=user).first()
            return {"exists":not (user_profile.premium_passcode==None)}
        
        except Exception as e:
            abort(500, f'An unexpected error occurred: {str(e)}')


@transaction_ns.route("/api/get_all_expense")
class Transactions(Resource):
    @transaction_ns.doc('get_all_transactions', description='Retrieve all Transaactions.', security='BearerAuth')
    @jwt_required()
    @transaction_ns.marshal_list_with(transaction_model, code=200)
    @transaction_ns.response(401, 'Unauthorized: Missing or invalid token', error_model)
    @transaction_ns.response(500, 'Unexpected error', error_model)
    @transaction_ns.response(404, 'User not exist', error_model)
    def get(self):
        try:
            user_id = get_jwt_identity()
            user = User.query.filter_by(user_id=user_id).first()
            if not user:
                abort(404, 'User not found')
            
            transactions=Transaction.query.filter_by(user_id=user).all()
            return {"expenses":[
                {"date":transaction.transaction_date,
                 "name":transaction.transaction_name,
                 "category":transaction.category,
                 "type":transaction.transaction_type,
                 "amount":transaction.amount}
                  for transaction in transactions]},200
        
        except Exception as e:
            abort(500, f'An unexpected error occurred: {str(e)}')

@transaction_ns.route("/get_all_categories")
class Categories(Resource):
    @transaction_ns.doc('get_all_categories', description='Retrieve all Transaactions Categories.', security='BearerAuth')
    @jwt_required()
    @transaction_ns.marshal_list_with(categories_model, code=202)
    @transaction_ns.response(401, 'Unauthorized: Missing or invalid token', error_model)
    @transaction_ns.response(404, 'User not exist', error_model)
    @transaction_ns.response(500, 'Unexpected error', error_model)
    def get(self):
        try:
            user_id = get_jwt_identity()
            user = User.query.filter_by(user_id=user_id).first()
            if not user:
                abort(404, 'User not found')
            
            transactions=Transaction.query.filter_by(user_id=user).all()
            return {"categories":[
                 transaction.category
                  for transaction in transactions]},200
        
        except Exception as e:
            abort(500, f'An unexpected error occurred: {str(e)}')



@transaction_ns.route("/add_expense")
class CreateTransaction(Resource):
    @transaction_ns.doc('add_expense', description='Add a Transaction', security='BearerAuth')
    @jwt_required()
    @transaction_ns.marshal_list_with(create_transaction_model, code=201)
    @transaction_ns.response(401, 'Unauthorized: Missing or invalid token', error_model)
    @transaction_ns.response(404, 'User not found', error_model)
    @transaction_ns.response(400, 'No transaction type', error_model)
    @transaction_ns.response(402, 'No transaction details', error_model)
    @transaction_ns.response(500, 'Unexpected error', error_model)
    def post(self):
        try:
            user_id = get_jwt_identity()
            user = User.query.filter_by(user_id=user_id).first()
            if not user:
                abort(404, 'User not found')
            data=transaction_ns.payload
            if not data.get("type"):
                abort(400,"Choose transaction type")
            if not data.get("name"):
                abort(402,"Enter transaction details")
            new_transaction=Transaction(
                transaction_type = data.get("type"),
                transaction_date=datetime.strptime(data.get("date"), '%Y-%m-%d').date(), 
                transaction_name=data.get("name"), 
                category=data.get("category"),
                amount=float(data.get("amount")),
                user_id=user,
                created_at=get_current_ist()   
            )
            db.session.add(new_transaction)
            db.session.commit()
            return {
                'type':new_transaction.transaction_type,
                'date':new_transaction.transaction_date,
                'name':new_transaction.transaction_name,
                'category':new_transaction.category,
                'amount':new_transaction.amount
            },201
        except Exception as e:
            db.session.rollback()
            abort(500, f'An unexpected error occurred: {str(e)}')