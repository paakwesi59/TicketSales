# services/ticket_service.py
import os
import uuid
import qrcode
from datetime import datetime
from flask import current_app
from models.ticket import Ticket
from app import db


def process_ticket_purchase(event, email, quantity):
    # Apply promotion rules
    discount = 0.0
    free_tickets = 0
    if event.bulk_min_tickets and event.bulk_discount_percent:
        if quantity >= event.bulk_min_tickets:
            discount = (event.bulk_discount_percent / 100.0) * (event.price * quantity)
    if event.free_ticket_min and event.free_tickets:
        if quantity >= event.free_ticket_min:
            free_tickets = event.free_tickets

    total_requested = quantity + free_tickets
    available = event.total_tickets - event.tickets_sold
    if total_requested > available:
        return {"success": False,
                "message": f"Only {available} tickets are available (including promotional free tickets)."}

    final_price = event.price * quantity - discount

    # Update sold count (including free tickets)
    event.tickets_sold += total_requested
    db.session.commit()

    tickets_generated = []

    def generate_ticket():
        ticket_code = str(uuid.uuid4())
        qr = qrcode.make(ticket_code)
        upload_path = os.path.join(current_app.root_path, 'static', 'tickets_qr')
        os.makedirs(upload_path, exist_ok=True)
        qr_filename = f"{ticket_code}.png"
        file_path = os.path.join(upload_path, qr_filename)
        qr.save(file_path)
        ticket = Ticket(
            ticket_code=ticket_code,
            event_id=event.id,
            purchaser_email=email,
            qr_code_filename=qr_filename
        )
        db.session.add(ticket)
        return ticket

    # Generate purchased tickets
    for _ in range(quantity):
        ticket = generate_ticket()
        tickets_generated.append(ticket)
    # Generate free tickets
    for _ in range(free_tickets):
        ticket = generate_ticket()
        tickets_generated.append(ticket)

    db.session.commit()

    return {
        "success": True,
        "tickets": tickets_generated,
        "discount": discount,
        "free_tickets": free_tickets,
        "final_price": final_price
    }
