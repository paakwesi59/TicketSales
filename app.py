# app.py
from flask import Flask
from config import Config
from extensions import db, bcrypt, mail, migrate, login_manager

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions with app
    db.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"  # Use the auth blueprint's login route

    # Import models so they are registered with SQLAlchemy
    from models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from routes.auth import auth as auth_blueprint
    from routes.events import events as events_blueprint
    from routes.tickets import tickets as tickets_blueprint

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(events_blueprint)
    app.register_blueprint(tickets_blueprint)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
