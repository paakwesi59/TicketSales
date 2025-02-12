# models/ticket.py
import uuid
from datetime import datetime
from models import db

class Ticket(db.Model):
    __tablename__ = 'ticket'
    id = db.Column(db.Integer, primary_key=True)
    ticket_code = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    purchaser_email = db.Column(db.String(120), nullable=False)
    purchase_time = db.Column(db.DateTime, default=datetime.utcnow)
    qr_code_filename = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<Ticket {self.ticket_code}>"
