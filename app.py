# app.py
from flask import Flask
from config import Config
from models import db  # Our SQLAlchemy instance & models
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "main.login"  # Using the 'main' blueprint
migrate = Migrate(app, db)
mail = Mail(app)

# Import the User model for the user loader
from models.user import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Register the blueprint from the routes package
from routes.main import main as main_blueprint
app.register_blueprint(main_blueprint)

if __name__ == "__main__":
    app.run(debug=True)
