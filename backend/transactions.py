# backend/transactions.py
from flask import Blueprint, request, jsonify
from auth import token_required
import jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from db import get_db

load_dotenv()

transactions_bp = Blueprint('transactions', __name__)

DEFAULT_CATEGORIES = {
    'food': 'Alimentação',
    'transport': 'Transporte',
    'housing': 'Moradia',
    'entertainment': 'Lazer',
    'health': 'Saúde',
    'education': 'Educação',
    'other': 'Outros'
}

SECRET_KEY = os.getenv('SECRET_KEY')
JWT_ALGORITHM = 'HS256'

def init_db():
    """Garante que a tabela existe ao iniciar"""
    with get_db() as db:
        db.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                description TEXT NOT NULL,
                amount REAL NOT NULL,
                type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
                category TEXT NOT NULL,
                date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        db.commit()
init_db()

@transactions_bp.route('/transactions', methods=['POST'])
@token_required
def add_transaction():
    try:
        token = request.headers['Authorization'].split()[1]
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id = decoded['user_id']
        
        data = request.get_json()
        required_fields = ['description', 'amount', 'type', 'category']
        if not all(field in data for field in required_fields):
            return jsonify({
                "error": "Missing fields",
                "required": required_fields,
                "received": list(data.keys())
            }), 400
            
        if data['type'] not in ['income', 'expense']:
            return jsonify({
                "error": "Invalid transaction type",
                "valid_types": ["income", "expense"]
            }), 400
            
        if data['category'] not in DEFAULT_CATEGORIES:
            return jsonify({
                "error": "Invalid category",
                "valid_categories": list(DEFAULT_CATEGORIES.keys())
            }), 400

        try:
            amount = float(data['amount'])
            if amount <= 0:
                return jsonify({"error": "Amount must be positive"}), 400
        except ValueError:
            return jsonify({"error": "Amount must be a number"}), 400

        with get_db() as db:
            cursor = db.execute(
                '''INSERT INTO transactions 
                (user_id, description, amount, type, category) 
                VALUES (?, ?, ?, ?, ?)''',
                (user_id, data['description'], amount, 
                 data['type'], data['category'])
            )
            db.commit()
            
            transaction = db.execute(
                '''SELECT id, description, amount, type, category, 
                   strftime('%Y-%m-%d %H:%M:%S', date) as date 
                FROM transactions WHERE id = ?''',
                (cursor.lastrowid,)
            ).fetchone()
            
            return jsonify({
                "message": "Transaction added successfully",
                "transaction": dict(transaction)
            }), 201
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@transactions_bp.route('/transactions', methods=['GET'])
@token_required
def get_transactions():
    try:
        # os parâmetros ficam aqui
        token = request.headers['Authorization'].split()[1]
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id = decoded['user_id']
        category = request.args.get('category')
        transaction_type = request.args.get('type')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        base_query = '''
            SELECT id, description, amount, type, category, 
                   strftime('%Y-%m-%d %H:%M:%S', date) as date 
            FROM transactions 
            WHERE user_id = ?
        '''
        params = [user_id]
        
        if category:
            base_query += ' AND category = ?'
            params.append(category)
            
        if transaction_type:
            base_query += ' AND type = ?'
            params.append(transaction_type)
            
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
                base_query += ' AND date >= ?'
                params.append(start_date)
            except ValueError:
                return jsonify({"error": "Invalid date format (use YYYY-MM-DD)"}), 400
                
        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
                base_query += ' AND date < ?'
                params.append(end_date)
            except ValueError:
                return jsonify({"error": "Invalid date format (use YYYY-MM-DD)"}), 400
        
        base_query += ' ORDER BY date DESC'
        
        with get_db() as db:
            transactions = db.execute(base_query, tuple(params)).fetchall()
            
            return jsonify({
                "count": len(transactions),
                "categories": DEFAULT_CATEGORIES,
                "transactions": [dict(t) for t in transactions]
            })
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@transactions_bp.route('/categories', methods=['GET'])
@token_required
def get_categories():
    return jsonify(DEFAULT_CATEGORIES)