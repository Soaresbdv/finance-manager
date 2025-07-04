from flask import Flask
from auth import auth_bp
# from backend.transactions_wait import transactions_bp

app = Flask(__name__)

app.register_blueprint(auth_bp, url_prefix='/api')

#app.register_blueprint(transactions_bp)

if __name__ == '__main__':
    app.run(debug=True)