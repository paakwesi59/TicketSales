from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail
from config import Config

# Initialize Flask app and load configuration
app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions with the app
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "main.login"  # Using blueprint 'main'
migrate = Migrate(app, db)
mail = Mail(app)

# Import models (ensure the User model is defined using the same db instance)
from models import User

# Set up user loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Import and register the blueprint (ensure your routes are organized under the 'main' blueprint)
from routes import main as main_blueprint
app.register_blueprint(main_blueprint)

if __name__ == "__main__":
    app.run(debug=True)
