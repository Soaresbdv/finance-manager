from flask import Blueprint, request, jsonify
import bcrypt
import jwt
import datetime
from database import get_db

auth_bp = Blueprint('auth', __name__)

SECRET_KEY = 'financeteste@'

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
        token = jwt.encode({
            'user_id': 1,  
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, SECRET_KEY)
        return jsonify({"token": token}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 401