from flask import Flask, jsonify, send_from_directory  # Adicione send_from_directory aqui
from auth import token_required, auth_bp
from transactions import transactions_bp
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(transactions_bp, url_prefix='/api')

@app.route('/api/validate-token', methods=['GET'])
@token_required
def validate_token():
    return jsonify({"valid": True}), 200

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