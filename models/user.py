# models/user.py
from flask_login import UserMixin
from itsdangerous import URLSafeTimedSerializer
from models import db

# Helper function to get a serializer using the app’s SECRET_KEY via current_app
def get_serializer():
    from flask import current_app
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"])

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    user_type = db.Column(db.String(50), nullable=False)  # e.g., 'event_organizer'
    confirmed = db.Column(db.Boolean, default=False)

    events = db.relationship('Event', backref='organizer', lazy=True)

    def __repr__(self):
        return f"<User {self.username}>"

    def generate_confirmation_token(self):
        serializer = get_serializer()
        return serializer.dumps(self.email, salt="email-confirmation-salt")

    @staticmethod
    def confirm_token(token, expiration=3600):
        serializer = get_serializer()
        try:
            email = serializer.loads(token, salt="email-confirmation-salt", max_age=expiration)
        except Exception:
            return False
        return email

    def generate_reset_token(self):
        serializer = get_serializer()
        return serializer.dumps(self.email, salt="password-reset-salt")

    @staticmethod
    def verify_reset_token(token, expiration=3600):
        serializer = get_serializer()
        try:
            email = serializer.loads(token, salt="password-reset-salt", max_age=expiration)
        except Exception:
            return False
        return email
