from flask import Flask
from app.config import Config

def create_app(config_class=Config):
    """Application factory function"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Import and register blueprints INSIDE the function
    from app.routes.dashboard import dashboard_bp
    from app.routes.api import api_bp
    
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(api_bp)
    
    return app