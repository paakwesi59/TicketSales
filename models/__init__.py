# models/__init__.py
from extensions import db

# Import models so they are registered with SQLAlchemy
from models.user import User
from models.event import Event
from models.ticket import Ticket
