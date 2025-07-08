from flask import Blueprint, request, jsonify
import re
import sqlite3
import bcrypt
from contextlib import contextmanager
from datetime import datetime, timedelta
from functools import wraps 

import jwt, os

auth_bp = Blueprint('auth', __name__)

SECRET_KEY = os.getenv('SECRET_KEY')  # Já deve existir
JWT_ALGORITHM = 'HS256'  # Adicione esta linha

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
    try:
        data = request.get_json()
        
        # Validações básicas
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({"error": "Email e senha são obrigatórios"}), 400
            
        if not re.match(r"[^@]+@[^@]+\.[^@]+", data['email']):
            return jsonify({"error": "Formato de email inválido"}), 400
            
        if len(data['password']) < 6:
            return jsonify({"error": "Senha deve ter pelo menos 6 caracteres"}), 400
        
        with get_db() as db:
            # Verifica se o email já existe
            # Modifique a query no register():
            if db.execute('SELECT email FROM users WHERE email = ?', (data['email'],)).fetchone():
                return jsonify({"error": "Email já cadastrado"}), 409            
            password_hash = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            db.execute(
                'INSERT INTO users (email, password_hash, name) VALUES (?, ?, ?)',
                (data['email'], password_hash, data.get('name', ''))
            )
            db.commit()      
            return jsonify({
                "message": "Usuário registrado com sucesso",
                "user": {
                    "email": data['email'],
                    "name": data.get('name', '')
                }
            }), 201
            
    except sqlite3.Error as e:
        return jsonify({"error": f"Erro no banco de dados: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({"error": "Email e senha são obrigatórios"}), 400

        with get_db() as db:
            user = db.execute(
                'SELECT id, email, password_hash FROM users WHERE email = ?',
                (data['email'],)
            ).fetchone()


            if not user:
                return jsonify({"error": "Credenciais inválidas"}), 401
            if not bcrypt.checkpw(data['password'].encode('utf-8'), user['password_hash'].encode('utf-8')):
                return jsonify({"error": "Credenciais inválidas"}), 401

            token = jwt.encode({
                'user_id': user['id'],  # Agora usando o ID correto
                'email': user['email'],
                'exp': datetime.utcnow() + timedelta(hours=24)
            }, SECRET_KEY, algorithm=JWT_ALGORITHM)

            return jsonify({
                "message": "Login realizado com sucesso",
                "token": token
            }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
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