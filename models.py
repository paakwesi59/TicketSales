from app import db, app
from flask_login import UserMixin
from itsdangerous import URLSafeTimedSerializer
from datetime import datetime

# Serializer for generating tokens
serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])


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
        return serializer.dumps(self.email, salt="email-confirmation-salt")

    @staticmethod
    def confirm_token(token, expiration=3600):
        try:
            email = serializer.loads(token, salt="email-confirmation-salt", max_age=expiration)
        except Exception:
            return False
        return email

    def generate_reset_token(self):
        return serializer.dumps(self.email, salt="password-reset-salt")

    @staticmethod
    def verify_reset_token(token, expiration=3600):
        try:
            email = serializer.loads(token, salt="password-reset-salt", max_age=expiration)
        except Exception:
            return False
        return email


class Event(db.Model):
    __tablename__ = 'event'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    event_date = db.Column(db.DateTime, nullable=False)
    price = db.Column(db.Float, nullable=False)
    total_tickets = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(255), nullable=True)  # stores filename of the event image
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"<Event {self.title} on {self.event_date}>"
