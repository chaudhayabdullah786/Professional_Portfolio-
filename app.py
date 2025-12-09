import os
import logging
import re
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
mail = Mail()

# create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///portfolio.db"
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Flask-Mail configuration
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', '587'))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')

# File upload configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Initialize extensions
db.init_app(app)
login_manager.init_app(app)
mail.init_app(app)

login_manager.login_view = 'admin.login'
login_manager.login_message = 'Please log in to access the admin panel.'

@login_manager.user_loader
def load_user(user_id):
    from models import AdminUser
    return AdminUser.query.get(int(user_id))

# Template context processors
from utils import get_setting

@app.context_processor
def inject_settings():
    from models import ContactMessage, Project, BlogPost, Skill
    return dict(
        get_setting=get_setting,
        ContactMessage=ContactMessage,
        Project=Project,
        BlogPost=BlogPost,
        Skill=Skill
    )

# Import routes
from routes import main, admin
app.register_blueprint(main.bp)
app.register_blueprint(admin.bp, url_prefix='/admin')

with app.app_context():
    # Import models to ensure tables are created
    import models
    db.create_all()

    # Create default admin user if none exists
    from models import AdminUser
    from werkzeug.security import generate_password_hash

    def create_admin_user():
        if not AdminUser.query.first():
            admin_user = AdminUser()
            admin_user.username = 'abdullah'
            admin_user.email = 'shawaiz@portfolio.com'
            admin_user.password_hash = generate_password_hash('231980077')
            db.session.add(admin_user)
            db.session.commit()
            print("Default admin user created: username='abdullah', password='231980077'")

    # Create admin user if it doesn't exist
    create_admin_user()

    # Add custom Jinja2 filters
    @app.template_filter('nl2br')
    def nl2br_filter(text):
        if text is None:
            return ''
        # Convert newlines to <br> tags
        return re.sub(r'\r\n|\r|\n', '<br>', str(text))