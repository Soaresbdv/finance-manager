from flask import Blueprint, request, jsonify
import re

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Validações
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({"error": "Email e senha são obrigatórios"}), 400
        
    if not re.match(r"[^@]+@[^@]+\.[^@]+", data['email']):
        return jsonify({"error": "Formato de email inválido"}), 400
        
    if len(data['password']) < 6:
        return jsonify({"error": "Senha deve ter pelo menos 6 caracteres"}), 400
    
    # Resposta de sucesso
    return jsonify({
        "message": "Usuário registrado com sucesso",
        "user": {"email": data['email']}
    }), 201