import os
import logging
import re
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

logging.basicConfig(level=logging.INFO)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
mail = Mail()

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# ✅ PostgreSQL (Railway)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Mail
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')

db.init_app(app)
login_manager.init_app(app)
mail.init_app(app)

login_manager.login_view = "admin.login"

@login_manager.user_loader
def load_user(user_id):
    from models import AdminUser
    return AdminUser.query.get(int(user_id))

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

from routes import main, admin
app.register_blueprint(main.bp)
app.register_blueprint(admin.bp, url_prefix="/admin")

# ✅ IMPORTANT: DO NOT auto-create tables in production
if os.environ.get("FLASK_ENV") != "production":
    with app.app_context():
        import models
        db.create_all()

        from models import AdminUser
        from werkzeug.security import generate_password_hash

        if not AdminUser.query.first():
            admin = AdminUser(
                username="abdullah",
                email="shawaiz@portfolio.com",
                password_hash=generate_password_hash("231980077")
            )
            db.session.add(admin)
            db.session.commit()

@app.template_filter("nl2br")
def nl2br(text):
    if not text:
        return ""
    return re.sub(r"\r\n|\r|\n", "<br>", str(text))
