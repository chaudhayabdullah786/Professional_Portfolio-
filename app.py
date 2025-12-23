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
# Logging
# --------------------------------------------------
logging.basicConfig(level=logging.INFO)

# --------------------------------------------------
# SQLAlchemy Base
# --------------------------------------------------
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
mail = Mail()

# --------------------------------------------------
# App
# --------------------------------------------------
app = Flask(__name__)
app.secret_key = os.environ.get(
    "SESSION_SECRET",
    "dev-secret-key-change-in-production"
)

app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# --------------------------------------------------
# DATABASE (Postgres preferred, fallback SQLite)
# --------------------------------------------------
DATABASE_URL ="postgresql://postgres:RUFpbWVaZgxAfLTpfdHlhtBSuwDSVNwI@yamanote.proxy.rlwy.net:10700/railway"

if DATABASE_URL:
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_pre_ping": True,
    "pool_recycle": 300,
}

# --------------------------------------------------
# Mail
# --------------------------------------------------
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')

# --------------------------------------------------
# Uploads
# --------------------------------------------------
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# --------------------------------------------------
# Init Extensions (ONLY ONCE)
# --------------------------------------------------
db.init_app(app)
login_manager.init_app(app)
mail.init_app(app)

login_manager.login_view = 'admin.login'
login_manager.login_message = 'Please log in to access the admin panel.'

# --------------------------------------------------
# User Loader
# --------------------------------------------------
@login_manager.user_loader
def load_user(user_id):
    from models import AdminUser
    return AdminUser.query.get(int(user_id))

# --------------------------------------------------
# Context Processor
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
# Routes
# --------------------------------------------------
from routes import main, admin
app.register_blueprint(main.bp)
app.register_blueprint(admin.bp, url_prefix="/admin")

# --------------------------------------------------
# Database Init (SAFE)
# --------------------------------------------------
with app.app_context():
    import models
    db.create_all()

    from models import AdminUser
    from werkzeug.security import generate_password_hash

    if not AdminUser.query.first():
        admin_user = AdminUser(
            username="abdullah",
            email="chaudhayabdullah786@gmail.com",
            password_hash=generate_password_hash("231980077")
        )
        db.session.add(admin_user)
        db.session.commit()
        logging.info("Default admin user created")

# --------------------------------------------------
# Jinja Filter
# --------------------------------------------------
@app.template_filter("nl2br")
def nl2br_filter(text):
    if not text:
        return ""
    return re.sub(r"\r\n|\r|\n", "<br>", str(text))

# --------------------------------------------------
# Run
# --------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
