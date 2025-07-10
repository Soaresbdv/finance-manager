from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import os

# Cria a instância do Flask primeiro
app = Flask(__name__)
CORS(app)

# Configurações
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'financeteste@')

# Importação dos blueprints (após criar o app)
from auth import auth_bp
from transactions import transactions_bp

# Registro dos blueprints
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(transactions_bp, url_prefix='/api')

# Rotas estáticas para o frontend
@app.route('/')
def serve_frontend():
    return send_from_directory('../frontend', 'index.html')

@app.route('/js/<path:filename>')
def serve_js(filename):
    return send_from_directory('../frontend/js', filename)

@app.route('/css/<path:filename>')
def serve_css(filename):
    return send_from_directory('../frontend/css', filename)

if __name__ == '__main__':
    app.run(debug=True)