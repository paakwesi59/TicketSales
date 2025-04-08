
# models/event.py
from datetime import datetime
from models import db

class Event(db.Model):
    __tablename__ = 'event'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    event_date = db.Column(db.DateTime, nullable=False)
    price = db.Column(db.Float, nullable=False)
    total_tickets = db.Column(db.Integer, nullable=False)
    tickets_sold = db.Column(db.Integer, default=0, nullable=False)
    image = db.Column(db.String(255), nullable=True)
    venue = db.Column(db.String(150), nullable=False)
    duration = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    bulk_min_tickets = db.Column(db.Integer, nullable=True)
    bulk_discount_percent = db.Column(db.Float, nullable=True)
    free_ticket_min = db.Column(db.Integer, nullable=True)
    free_tickets = db.Column(db.Integer, nullable=True)

    tickets = db.relationship('Ticket', backref='event', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Event {self.title} on {self.event_date}>"
