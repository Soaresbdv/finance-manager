from flask import Blueprint, request, jsonify
from database import get_db
from functools import wraps
import jwt
import datetime

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

def check_budget_alerts(user_id, amount, category):
    with get_db() as db:
        category_limit = db.execute('''
            SELECT monthly_limit FROM category_limits
            WHERE user_id = ? AND category = ?
        ''', (user_id, category)).fetchone()

        if category_limit:
            monthly_spent = db.execute('''
                SELECT SUM(amount) as total FROM transactions
                WHERE user_id = ? AND category = ? 
                AND strftime('%Y-%m', date) = strftime('%Y-%m', 'now')
            ''', (user_id, category)).fetchone()

            if monthly_spent['total'] + amount > category_limit['monthly_limit']:
                return "Você excedeu o limite desta categoria!"

        return None
    
def is_valid_category(category, transaction_type):
    """Verifica se a categoria é válida para o tipo especificado"""
    return category in CATEGORIES.get(transaction_type, [])

@transactions_bp.route('/transactions', methods=['POST'])
@token_required
def add_transaction(current_user_id):
    try:
        data = request.get_json()
        
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

        try:
            amount = float(data['amount'])
            if amount <= 0:
                return jsonify({"error": "Valor deve ser positivo"}), 400
        except ValueError:
            return jsonify({"error": "Valor inválido"}), 400

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
        period = request.args.get('period', 'all')  
        months = int(request.args.get('months', 1))  
        category = request.args.get('category')      
        transaction_type = request.args.get('type')  
        
        base_query = '''
            SELECT id, description, amount, type, category, 
                   strftime('%Y-%m-%d %H:%M:%S', date) as date 
            FROM transactions 
            WHERE user_id = ?
        '''
        params = [current_user_id]
        
        if period != 'all':
            date_filters = {
                'day': "date >= datetime('now', 'start of day')",
                'week': "date >= datetime('now', '-6 days', 'start of day')",
                'month': "strftime('%Y-%m', date) = strftime('%Y-%m', 'now')",
                'year': "strftime('%Y', date) = strftime('%Y', 'now')",
                'custom': f"date >= datetime('now', '-{months} months')"
            }
            base_query += f" AND {date_filters.get(period, date_filters['custom'])}"
        
        if category:
            base_query += " AND category = ?"
            params.append(category)
            
        if transaction_type:
            base_query += " AND type = ?"
            params.append(transaction_type)
        
        base_query += " ORDER BY date DESC"
        
        with get_db() as db:
            transactions = db.execute(base_query, tuple(params)).fetchall()
            
            return jsonify({
                "count": len(transactions),
                "transactions": [dict(t) for t in transactions],
                "filters": {
                    "period": period,
                    "months": months if period == 'custom' else None,
                    "category": category,
                    "type": transaction_type
                }
            }), 200
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@transactions_bp.route('/transactions/stats', methods=['GET'])
@token_required
def get_stats(current_user_id):
    try:
        months = int(request.args.get('months', 6))  
        
        with get_db() as db:
            stats = db.execute('''
                SELECT category, type, 
                       SUM(amount) as total,
                       strftime('%Y-%m', date) as month
                FROM transactions
                WHERE user_id = ? 
                AND date >= datetime('now', '-? months')
                GROUP BY category, type, strftime('%Y-%m', date)
                ORDER BY month DESC
            ''', (current_user_id, months)).fetchall()
            
            monthly_totals = db.execute('''
                SELECT 
                    strftime('%Y-%m', date) as month,
                    SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) as income,
                    SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) as expense
                FROM transactions
                WHERE user_id = ?
                AND date >= datetime('now', '-? months')
                GROUP BY strftime('%Y-%m', date)
                ORDER BY month DESC
            ''', (current_user_id, months)).fetchall()
            
            return jsonify({
                "category_stats": [dict(s) for s in stats],
                "monthly_totals": [dict(m) for m in monthly_totals],
                "period_months": months
            }), 200
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@transactions_bp.route('/weekly-summary', methods=['GET'])
@token_required
def weekly_summary(current_user_id):
    with get_db() as db:
        salary = db.execute('''
            SELECT amount FROM user_salary WHERE user_id = ?
        ''', (current_user_id,)).fetchone()

        if not salary:
            return jsonify({"error": "Salário não cadastrado"}), 400

        weekly_budget = (salary['amount'] / 4)  

        expenses = db.execute('''
            SELECT SUM(amount) as total
            FROM transactions
            WHERE user_id = ? 
            AND type = 'expense'
            AND date >= datetime('now', 'weekday 0', '-7 days')
        ''', (current_user_id,)).fetchone()

        remaining_days = 7 - datetime.now().weekday()
        projected = (expenses['total'] or 0) / (7 - remaining_days) * 7

        return jsonify({
            "weekly_budget": weekly_budget,
            "spent_this_week": expenses['total'] or 0,
            "projected_spending": projected,
            "remaining_budget": weekly_budget - (expenses['total'] or 0),
            "alert": projected > weekly_budget * 1.1  # 10% acima do orçamento
        })

@transactions_bp.route('/spending-habits', methods=['GET'])
@token_required
def spending_habits(current_user_id):
    with get_db() as db:
        habits = db.execute('''
            SELECT 
                strftime('%w', date) as weekday,
                AVG(amount) as avg_spending,
                COUNT(*) as frequency
            FROM transactions
            WHERE user_id = ? AND type = 'expense'
            GROUP BY strftime('%w', date)
        ''', (current_user_id,)).fetchall()
        
        return jsonify({"habits": [dict(h) for h in habits]})

@transactions_bp.route('/categories', methods=['GET'])
def get_categories():
    return jsonify(CATEGORIES), 200