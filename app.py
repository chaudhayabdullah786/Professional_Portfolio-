import os
import logging
import re
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# --------------------------------------------------
# LOGGING
# --------------------------------------------------
logging.basicConfig(level=logging.DEBUG)

# --------------------------------------------------
# SQLALCHEMY BASE
# --------------------------------------------------
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
mail = Mail()

# --------------------------------------------------
# CREATE FLASK APP
# --------------------------------------------------
app = Flask(__name__)
app.secret_key = os.environ.get(
    "SESSION_SECRET",
    "dev-secret-key-change-in-production"
)

app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# --------------------------------------------------
# DATABASE CONFIG
# (SQLite default – PostgreSQL if env variable exists)
# --------------------------------------------------
DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    # PostgreSQL (Neon / Production)
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
else:
    # SQLite (OLD PROJECT DATABASE)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///portfolio.db"

app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# --------------------------------------------------
# MAIL CONFIG
# --------------------------------------------------
app.config["MAIL_SERVER"] = os.environ.get(
    "MAIL_SERVER", "smtp.gmail.com"
)
app.config["MAIL_PORT"] = int(
    os.environ.get("MAIL_PORT", "587")
)
app.config["MAIL_USE_TLS"] = os.environ.get(
    "MAIL_USE_TLS", "true"
).lower() in ["true", "on", "1"]

app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"] = os.environ.get(
    "MAIL_DEFAULT_SENDER"
)

# --------------------------------------------------
# FILE UPLOAD CONFIG
# --------------------------------------------------
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB
app.config["UPLOAD_FOLDER"] = "static/uploads"

# --------------------------------------------------
# INIT EXTENSIONS (ONLY ONCE)
# --------------------------------------------------
db.init_app(app)
login_manager.init_app(app)
mail.init_app(app)

# --------------------------------------------------
# LOGIN MANAGER
# --------------------------------------------------
login_manager.login_view = "admin.login"
login_manager.login_message = "Please log in to access the admin panel."

@login_manager.user_loader
def load_user(user_id):
    from models import AdminUser
    return AdminUser.query.get(int(user_id))

# --------------------------------------------------
# CONTEXT PROCESSOR
# --------------------------------------------------
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

# --------------------------------------------------
# ROUTES / BLUEPRINTS
# --------------------------------------------------
from routes import main, admin

app.register_blueprint(main.bp)
app.register_blueprint(admin.bp, url_prefix="/admin")

# --------------------------------------------------
# DATABASE INIT (SAFE – NO DATA LOSS)
# --------------------------------------------------
with app.app_context():
    import models

    # ❗ SAFE: tables create hongi, delete NAHI
    db.create_all()

    from models import AdminUser
    from werkzeug.security import generate_password_hash

    # Create admin only if not exists
    if not AdminUser.query.first():
        admin_user = AdminUser(
            username="abdullah",
            email="shawaiz@portfolio.com",
            password_hash=generate_password_hash("231980077")
        )
        db.session.add(admin_user)
        db.session.commit()
        print("✅ Default admin user created")

# --------------------------------------------------
# JINJA FILTER
# --------------------------------------------------
@app.template_filter("nl2br")
def nl2br_filter(text):
    if text is None:
        return ""
    return re.sub(r"\r\n|\r|\n", "<br>", str(text))
