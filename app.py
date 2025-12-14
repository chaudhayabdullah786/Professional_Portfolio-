import os
import logging
import re

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import generate_password_hash

# -------------------------------------------------
# Logging
# -------------------------------------------------
logging.basicConfig(level=logging.INFO)

# -------------------------------------------------
# SQLAlchemy Base
# -------------------------------------------------
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
mail = Mail()

# -------------------------------------------------
# Flask App
# -------------------------------------------------
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

# Fix reverse proxy issues (PythonAnywhere / Render / Nginx)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# -------------------------------------------------
# Database Configuration (SAFE)
# -------------------------------------------------
DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    # Neon / PostgreSQL
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
else:
    # Local fallback (NO DATA LOSS)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///portfolio.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_pre_ping": True,
    "pool_recycle": 300,
}

# -------------------------------------------------
# Flask-Mail
# -------------------------------------------------
app.config["MAIL_SERVER"] = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
app.config["MAIL_PORT"] = int(os.environ.get("MAIL_PORT", 587))
app.config["MAIL_USE_TLS"] = os.environ.get("MAIL_USE_TLS", "true").lower() in ("true", "1")
app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"] = os.environ.get("MAIL_DEFAULT_SENDER")

# -------------------------------------------------
# Uploads
# -------------------------------------------------
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
app.config["UPLOAD_FOLDER"] = "static/uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# -------------------------------------------------
# Init Extensions
# -------------------------------------------------
db.init_app(app)
login_manager.init_app(app)
mail.init_app(app)

login_manager.login_view = "admin.login"
login_manager.login_message = "Please log in to access the admin panel."

# -------------------------------------------------
# User Loader (SAFE)
# -------------------------------------------------
@login_manager.user_loader
def load_user(user_id):
    from models import AdminUser
    return db.session.get(AdminUser, int(user_id))

# -------------------------------------------------
# Context Processor (Old Project SAFE)
# -------------------------------------------------
from utils import get_setting

@app.context_processor
def inject_globals():
    from models import ContactMessage, Project, BlogPost, Skill
    return dict(
        get_setting=get_setting,
        ContactMessage=ContactMessage,
        Project=Project,
        BlogPost=BlogPost,
        Skill=Skill,
    )

# -------------------------------------------------
# Routes / Blueprints
# -------------------------------------------------
from routes import main, admin

app.register_blueprint(main.bp)
app.register_blueprint(admin.bp, url_prefix="/admin")

# -------------------------------------------------
# App Startup Tasks
# -------------------------------------------------
with app.app_context():
    import models

    # ✅ Create tables (NO deletion)
    db.create_all()

    # ✅ Ensure Admin Exists
    from models import AdminUser

    if not AdminUser.query.first():
        admin = AdminUser(
            username="abdullah",
            email="chaudhayabdullah786@gmail.com",
            password_hash=generate_password_hash("231980077"),
        )
        db.session.add(admin)
        db.session.commit()
        logging.info("Default admin user created")

# -------------------------------------------------
# Jinja Filter
# -------------------------------------------------
@app.template_filter("nl2br")
def nl2br_filter(text):
    if not text:
        return ""
    return re.sub(r"\r\n|\r|\n", "<br>", str(text))

# -------------------------------------------------
# Run
# -------------------------------------------------
if __name__ == "__main__":
    app.run(debug=False)
