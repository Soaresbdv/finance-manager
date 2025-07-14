from flask import Flask, jsonify, send_from_directory, request, redirect, session, make_response
from flask_cors import CORS
from auth import auth_bp
from transactions import transactions_bp
import os
import jwt

app = Flask(__name__)
CORS(app)

app.secret_key = 'admin123'
SECRET_KEY = 'financeteste@'  # Mesma chave para JWT
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(transactions_bp, url_prefix='/api')

@app.route('/')
def serve_frontend():
    return send_from_directory('../frontend', 'index.html')

@app.route('/stats')
def get_stats():
    return jsonify({"message": "Estatísticas gerais"})

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('../frontend', filename)

@app.route('/css/<path:filename>')
def serve_css(filename):
    return send_from_directory('../frontend/css', filename)

@app.route('/js/<path:filename>')
def serve_js(filename):
    return send_from_directory('../frontend/js', filename)

@app.route('/dashboard')
def dashboard():
    token = request.args.get('token') or request.cookies.get('auth_token')
    
    if not token:
        return redirect('/?error=no_token')

    try:
        # Remove 'Bearer ' se existir
        token = token.replace('Bearer ', '')
        
        # Verificação explícita do token
        payload = jwt.decode(
            token,
            'financeteste@',  # Use a string diretamente para evitar conflitos
            algorithms=["HS256"],
            options={"verify_signature": True}
        )
        
        response = make_response(send_from_directory('../frontend', 'dashboard.html'))
        response.set_cookie(
            'auth_token',
            token,
            httponly=True,
            max_age=86400
        )
        return response
        
    except jwt.ExpiredSignatureError:
        return redirect('/?error=token_expired')
    except jwt.InvalidTokenError as e:
        print(f"Falha na verificação: {str(e)}")
        return redirect('/?error=invalid_token')

@app.route('/set-token', methods=['POST'])
def set_token():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        return jsonify({"error": "Token missing"}), 401
    
    response = jsonify({"message": "Token set"})
    response.set_cookie(
        'auth_token',
        token,
        httponly=True,
        max_age=86400
    )
    return response

if __name__ == '__main__':
    app.run(debug=True)