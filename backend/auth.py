from flask import Blueprint, request, jsonify
import re
import sqlite3
import bcrypt
from contextlib import contextmanager
from datetime import datetime, timedelta
import jwt
from functools import wraps 

auth_bp = Blueprint('auth', __name__)

SECRET_KEY = "finance@123" # atualizar futuramente para o meu .env, por enquanto deixar hardcode
TOKEN_EXPIRATION = 1 

@contextmanager
def get_db():
    conn = sqlite3.connect('finance.db')
    conn.row_factory = sqlite3.Row 
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with get_db() as db:
        db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                email TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL
            )
        ''')

init_db()

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({"error": "Email e senha são obrigatórios"}), 400

    if not re.match(r"[^@]+@[^@]+\.[^@]+", data['email']):
        return jsonify({"error": "Formato de email inválido"}), 400
        
    if len(data['password']) < 6:
        return jsonify({"error": "Senha deve ter pelo menos 6 caracteres"}), 400
    
    try:
        with get_db() as db:
            if db.execute('SELECT email FROM users WHERE email = ?', (data['email'],)).fetchone():
                return jsonify({"error": "Email já cadastrado"}), 409
            
            password_hash = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            db.execute(
                'INSERT INTO users (email, password_hash) VALUES (?, ?)',
                (data['email'], password_hash)
            )
            db.commit()
            
            return jsonify({
                "message": "Usuário registrado com sucesso",
                "user": {"email": data['email']}
            }), 201
            
    except sqlite3.Error as e:
        return jsonify({"error": f"Erro no banco de dados: {str(e)}"}), 500
    
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    with get_db() as db:
        user = db.execute('SELECT * FROM users WHERE email = ?', (data['email'],)).fetchone()
        
        if not user or not bcrypt.checkpw(data['password'].encode('utf-8'), user['password_hash'].encode('utf-8')):
            return jsonify({"error": "Credenciais inválidas"}), 401
            
        token = jwt.encode({
            'user_id': user['id'],  # Agora incluímos o ID
            'email': user['email'],
            'exp': datetime.utcnow() + timedelta(hours=2)
        }, SECRET_KEY, algorithm="HS256")
        
        return jsonify({"token": token, "user_id": user['id']})
    
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"error": "Token ausente"}), 401
            
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expirado"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Token inválido"}), 401
            
        return f(*args, **kwargs)
    return decorated