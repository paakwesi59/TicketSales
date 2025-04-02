# routes/tickets.py
import os
import io
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, send_file
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from extensions import db
from models.ticket import Ticket
from models.event import Event
from services.ticket_service import process_ticket_purchase
from services.email_service import send_ticket_email

tickets = Blueprint('tickets', __name__)

@tickets.route("/event/<int:event_id>/buy", methods=["GET", "POST"])
def buy_ticket(event_id):
    from forms.forms import TicketPurchaseForm  # Local import if necessary
    event = Event.query.get_or_404(event_id)
    form = TicketPurchaseForm()
    if form.validate_on_submit():
        quantity = form.quantity.data
        # You may delegate price calculations to the service
        return render_template("checkout.html",
                               event=event,
                               email=form.email.data,
                               quantity=quantity,
                               total_price=event.price * quantity,
                               discount=0,  # handled in service
                               free_tickets=0,
                               final_price=event.price * quantity)
    return render_template("buy_ticket.html", form=form, event=event)

@tickets.route("/checkout/confirm/<int:event_id>", methods=["POST"])
def confirm_purchase(event_id):
    event = Event.query.get_or_404(event_id)
    email = request.form.get("email")
    try:
        quantity = int(request.form.get("quantity"))
    except (ValueError, TypeError):
        flash("Invalid quantity.", "danger")
        return redirect(url_for("tickets.buy_ticket", event_id=event.id))

    result = process_ticket_purchase(event, email, quantity)
    if not result.get("success"):
        flash(result.get("message", "Ticket purchase failed."), "danger")
        return redirect(url_for("tickets.buy_ticket", event_id=event.id))

    tickets_generated = result.get("tickets")
    discount = result.get("discount", 0.0)
    free_tickets = result.get("free_tickets", 0)
    final_price = result.get("final_price", 0.0)

    try:
        send_ticket_email(email, event, quantity, tickets_generated)
    except Exception as e:
        current_app.logger.error(f"Error sending ticket email: {e}")
        flash("Tickets purchased successfully, but there was an error sending the confirmation email.", "danger")
    else:
        flash(f"Tickets purchased successfully! You received {free_tickets} free ticket(s). Total Price: GHC{final_price:.2f}. Check your email for details.", "success")

    return render_template("purchase_confirmation.html", event=event, tickets=tickets_generated,
                           quantity=quantity, discount=discount, free_tickets=free_tickets, final_price=final_price)

@tickets.route("/ticket/<int:ticket_id>/download")
def download_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    token = request.args.get('token')
    if not token or token != ticket.ticket_code:
        flash("Invalid token or unauthorized access to ticket.", "danger")
        return redirect(url_for("events.event_detail", event_id=ticket.event_id))
    event = Event.query.get(ticket.event_id)
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    pdf.setTitle(f"{event.title} Ticket")
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawCentredString(width / 2, height - 50, f"{event.title} Ticket")

    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, height - 100, f"Ticket Code: {ticket.ticket_code}")
    pdf.drawString(50, height - 120, f"Event Date & Time: {event.event_date.strftime('%B %d, %Y %I:%M %p')}")
    pdf.drawString(50, height - 140, f"Venue: {event.venue}")
    pdf.drawString(50, height - 160, f"Purchaser Email: {ticket.purchaser_email}")
    pdf.drawString(50, height - 180, f"Purchase Time: {ticket.purchase_time.strftime('%B %d, %Y %I:%M %p')}")

    qr_image_path = os.path.join(current_app.root_path, 'static', 'tickets_qr', ticket.qr_code_filename)
    if os.path.exists(qr_image_path):
        pdf.drawImage(qr_image_path, width - 220, height - 250, width=150, height=150)

    pdf.showPage()
    pdf.save()
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, mimetype='application/pdf',
                     download_name=f"{event.title}_ticket_{ticket.ticket_code}.pdf")
