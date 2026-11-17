import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'e-commerce.db')
app.config['SECRET_KEY'] = 's3cretK3y'
app.config['SESSION_PERMANENT'] = False

print(f"[DEBUG] DB path: {app.config['SQLALCHEMY_DATABASE_URI']}")

db = SQLAlchemy(app)
try:
    with app.app_context():
        db.create_all()
        print("[DEBUG] Database initialized successfully.")
except Exception as e:
    print("[ERROR] Database init failed:", e)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'LoginPage'
login_manager.login_message_category = 'info'

from Market import routes
