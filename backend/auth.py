from flask import Blueprint, request, jsonify

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()    
    return jsonify({
        'message': 'Usuário registrado com sucesso',
        'user': {'email': data['email']}
    }), 201