from flask import Blueprint, request, jsonify
import bcrypt
import jwt
import datetime
from database import get_db

# Blueprint deve ser a primeira coisa definida no arquivo
auth_bp = Blueprint('auth', __name__)

SECRET_KEY = 'financeteste@'  # Use a mesma chave do app.py

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        # Sua lógica de registro aqui
        return jsonify({"message": "Usuário registrado"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        # Sua lógica de login aqui
        token = jwt.encode({
            'user_id': 1,  # Substitua pelo ID real do usuário
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, SECRET_KEY)
        return jsonify({"token": token}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 401