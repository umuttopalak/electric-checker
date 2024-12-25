from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from flasgger import Swagger
import telegram
from config import Config

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
bot = None

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    
    # Initialize Swagger
    swagger = Swagger(app, 
        template = {
        'title': 'Electric Checker API',
        'uiversion': 3,
        'specs_route': '/swagger/',
        'openapi': '3.0.2',
        'static_url_path': '/flasgger_static',
        'swagger_ui': True
    })
    
    global bot
    bot = telegram.Bot(token=Config.TELEGRAM_TOKEN)

    # Register blueprints
    from app.routes.admin import admin_bp
    from app.routes.user import user_bp
    from app.routes.telegram import telegram_bp
    from app.routes.root import root_bp

    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(telegram_bp, url_prefix='/telegram')
    app.register_blueprint(root_bp, url_prefix='/')
    return app 