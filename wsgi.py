# /home/yourusername/myproject/wsgi.py
import sys, os

project_home = '/home/yourusername/myproject'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# If using a virtualenv, adjust os.environ if needed (optional here)
# os.environ['YOUR_ENV_VAR'] = 'value'

# Import your Flask app (example)
# If your app is in myproject/app.py and the Flask instance is named "app":
from app import app as application

# OR if using package myproject and create_app pattern:
# from myproject import create_app
# application = create_app()
