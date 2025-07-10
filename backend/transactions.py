from flask import Blueprint, request, jsonify
from database import get_db
from functools import wraps
import jwt

transactions_bp = Blueprint('transactions', __name__)

CATEGORIES = {
    'income': ['salary', 'bonus', 'freelance', 'other'],
    'expense': ['food', 'transport', 'housing', 'entertainment', 'health', 'education', 'other']
}

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"error": "Token ausente"}), 401
            
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            payload = jwt.decode(token, 'financeteste@', algorithms=["HS256"])
            kwargs['current_user_id'] = payload['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expirado"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Token inválido"}), 401
            
        return f(*args, **kwargs)
    return decorated

def is_valid_category(category, transaction_type):
    """Verifica se a categoria é válida para o tipo especificado"""
    return category in CATEGORIES.get(transaction_type, [])

@transactions_bp.route('/transactions', methods=['POST'])
@token_required
def add_transaction(current_user_id):
    try:
        data = request.get_json()
        
        # Validação dos campos
        required_fields = ['description', 'amount', 'type', 'category']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Campos obrigatórios faltando"}), 400
            
        if data['type'] not in ['income', 'expense']:
            return jsonify({"error": "Tipo de transação inválido"}), 400
            
        if not is_valid_category(data['category'], data['type']):
            return jsonify({
                "error": "Categoria inválida para este tipo de transação",
                "valid_categories": CATEGORIES.get(data['type'], [])
            }), 400

        # Conversão e validação do valor
        try:
            amount = float(data['amount'])
            if amount <= 0:
                return jsonify({"error": "Valor deve ser positivo"}), 400
        except ValueError:
            return jsonify({"error": "Valor inválido"}), 400

        # Inserção no banco de dados
        with get_db() as db:
            db.execute(
                '''INSERT INTO transactions 
                (user_id, description, amount, type, category) 
                VALUES (?, ?, ?, ?, ?)''',
                (current_user_id, data['description'], amount, 
                 data['type'], data['category'])
            )
            db.commit()
            
            return jsonify({"message": "Transação criada com sucesso"}), 201
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@transactions_bp.route('/transactions', methods=['GET'])
@token_required
def get_transactions(current_user_id):
    try:
        with get_db() as db:
            transactions = db.execute(
                '''SELECT id, description, amount, type, category, 
                   strftime('%Y-%m-%d %H:%M:%S', date) as date 
                FROM transactions 
                WHERE user_id = ?
                ORDER BY date DESC''',
                (current_user_id,)
            ).fetchall()
            
            return jsonify({
                "transactions": [dict(t) for t in transactions]
            }), 200
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@transactions_bp.route('/categories', methods=['GET'])
def get_categories():
    return jsonify(CATEGORIES), 200