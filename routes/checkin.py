# routes/checkin.py
import os
from datetime import datetime
from flask import Blueprint, request, jsonify, render_template, current_app
from flask_login import login_required, current_user
from models.ticket import Ticket
from models.event import Event
from extensions import db

checkin = Blueprint('checkin', __name__)

@checkin.route("/checkin", methods=["GET"])
@login_required
def checkin_page():
    # Only event organizers can access this page.
    if current_user.user_type != "event_organizer":
        return "Unauthorized", 403

    # Fetch the event associated with the current user (event organizer)
    event = Event.query.filter_by(created_by=current_user.id).first()
    if not event:
        return "No event found for the organizer", 400

    return render_template("checkin.html", event=event)

@checkin.route("/api/attendance/<int:event_id>", methods=["GET"])
@login_required
def live_attendance(event_id):
    event = Event.query.get_or_404(event_id)
    if event.created_by != current_user.id:
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    total_tickets = event.total_tickets
    tickets_checked_in = Ticket.query.filter_by(event_id=event_id, is_checked_in=True).count()
    return jsonify({
        "success": True,
        "total_tickets": total_tickets,
        "tickets_checked_in": tickets_checked_in,
        "tickets_remaining": total_tickets - tickets_checked_in
    })

@checkin.route("/api/checkin", methods=["POST"])
@login_required
def validate_qr_code():
    if current_user.user_type != "event_organizer":
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    ticket_code = request.json.get("ticket_code")
    ticket = Ticket.query.filter_by(ticket_code=ticket_code).first()

    if not ticket:
        return jsonify({"success": False, "message": "Invalid ticket."})

    event = Event.query.get(ticket.event_id)
    if event.created_by != current_user.id:
        return jsonify({"success": False, "message": "You do not have permission to check in this ticket."})

    if ticket.is_checked_in:
        return jsonify({
            "success": True,
            "already_checked_in": True,
            "check_in_time": ticket.check_in_time.strftime('%Y-%m-%d %H:%M:%S')
        })

    ticket.is_checked_in = True
    ticket.check_in_time = datetime.utcnow()
    db.session.commit()

    return jsonify({"success": True, "message": "Check-in successful!"})
