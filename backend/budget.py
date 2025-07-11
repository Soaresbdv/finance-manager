from flask import Blueprint, request, jsonify
from database import get_db
from datetime import datetime
from auth import token_required

budget_bp = Blueprint('budget', __name__)

@budget_bp.route('/salary', methods=['POST'])
@token_required
def set_salary(current_user_id):
    data = request.get_json()

    required_fields = ['amount', 'payment_day']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Campos obrigatórios: amount e payment_day"}), 400

    with get_db() as db:
        db.execute('''
            INSERT OR REPLACE INTO user_salary 
            (user_id, amount, payment_day, updated_at) 
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ''', (current_user_id, data['amount'], data['payment_day']))
        db.commit()

    return jsonify({"message": "Salário atualizado com sucesso"}), 200

@budget_bp.route('/category-limits', methods=['POST'])
@token_required
def set_category_limits(current_user_id):
    data = request.get_json() 
    
    with get_db() as db:
        for category, limit in data.items():
            db.execute('''
                INSERT OR REPLACE INTO category_limits
                (user_id, category, monthly_limit)
                VALUES (?, ?, ?)
            ''', (current_user_id, category, limit))
        db.commit()
    
    return jsonify({"message": "Limites atualizados"}), 200