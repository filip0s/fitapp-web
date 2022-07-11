from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
import os

# Inicializace aplikace
load_dotenv()
app = Flask(__name__)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.getenv("FITAPP_SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///fitapp.db"
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = "login_page"
login_manager.login_message = "Pro pokračování se musíte přihlásit"


# Import cest
from fitapp import views
