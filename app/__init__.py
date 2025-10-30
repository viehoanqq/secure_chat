# app.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from flask_cors import CORS

from .config import Config

db = SQLAlchemy()
jwt = JWTManager()
socketio = SocketIO(cors_allowed_origins="*")

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)

    db.init_app(app)
    jwt.init_app(app)
    socketio.init_app(app)

    # import routes
    from routes.auth_routes import auth_bp
    from routes.chat_routes import chat_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(chat_bp, url_prefix="/chat")

    with app.app_context():
        db.create_all()

    return app

app = create_app()

if __name__ == "__main__":
    socketio.run(app, debug=True)
