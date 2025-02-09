# from flask_login import UserMixin
# from app import db  # Import db instance from app
#
# class User(db.Model, UserMixin):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(150), unique=True, nullable=False)
#     email = db.Column(db.String(120), unique=True, nullable=False)
#     password = db.Column(db.String(255), nullable=False)
#     user_type = db.Column(db.String(50), nullable=False)
#
#     def __repr__(self):
#         return f"<User {self.username}>"

from flask import current_app
from flask_login import UserMixin
from itsdangerous import URLSafeTimedSerializer
from app import db  # Ensure this db instance is the one initialized in app.py


class User(db.Model, UserMixin):
    __tablename__ = "user"  # Explicit table name

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    user_type = db.Column(db.String(50), nullable=False)  # e.g., 'event_organizer'
    confirmed = db.Column(db.Boolean, default=False)  # For email verification

    def __repr__(self):
        return f"<User {self.username}>"

    @property
    def serializer(self):
        """
        Lazily creates a URLSafeTimedSerializer using the app's secret key.
        This property requires an active application context.
        """
        return URLSafeTimedSerializer(current_app.config["SECRET_KEY"])

    def generate_confirmation_token(self):
        """Generate a confirmation token for the user's email."""
        return self.serializer.dumps(self.email, salt="email-confirmation-salt")

    @staticmethod
    def confirm_token(token, expiration=3600):
        """
        Verify a confirmation token. Returns the email if valid, else False.
        Requires an active application context.
        """
        serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        try:
            email = serializer.loads(token, salt="email-confirmation-salt", max_age=expiration)
        except Exception:
            return False
        return email

    def generate_reset_token(self):
        """Generate a password reset token for the user."""
        return self.serializer.dumps(self.email, salt="password-reset-salt")

    @staticmethod
    def verify_reset_token(token, expiration=3600):
        """
        Verify a password reset token. Returns the email if valid, else False.
        Requires an active application context.
        """
        serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        try:
            email = serializer.loads(token, salt="password-reset-salt", max_age=expiration)
        except Exception:
            return False
        return email
