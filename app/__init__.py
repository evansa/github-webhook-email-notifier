from flask import Flask
from app.webhook import webhook_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")
    app.register_blueprint(webhook_bp)
    return app