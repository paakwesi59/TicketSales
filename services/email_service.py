# services/email_service.py
from flask_mail import Message
from flask import url_for, current_app
from app import mail

def send_confirmation_email(user):
    token = user.generate_confirmation_token()
    confirm_url = url_for("main.confirm_email", token=token, _external=True)
    subject = "Please confirm your email"
    msg = Message(subject,
                  sender=current_app.config["MAIL_DEFAULT_SENDER"],
                  recipients=[user.email])
    msg.body = f"Hello {user.username},\n\nPlease confirm your email by clicking the following link:\n{confirm_url}\n\nThank you!"
    mail.send(msg)

def send_reset_email(user):
    token = user.generate_reset_token()
    reset_url = url_for("main.reset_password", token=token, _external=True)
    subject = "Password Reset Request"
    msg = Message(subject,
                  sender=current_app.config["MAIL_DEFAULT_SENDER"],
                  recipients=[user.email])
    msg.body = f"Hello {user.username},\n\nTo reset your password, please click the link below:\n{reset_url}\n\nIf you did not request a password reset, please ignore this email."
    mail.send(msg)

def send_ticket_email(user_email, event, quantity, tickets):
    subject = f"Your Ticket Purchase for {event.title}"
    msg = Message(subject,
                  sender=current_app.config["MAIL_DEFAULT_SENDER"],
                  recipients=[user_email])
    ticket_details = "\n".join(
        [f"Ticket Code: {t.ticket_code} - Download: {url_for('main.download_ticket', ticket_id=t.id, _external=True)}"
         for t in tickets]
    )
    msg.body = f"""Hello,

You have successfully purchased {quantity} ticket(s) for the event:
Title: {event.title}
Description: {event.description}
Venue: {event.venue}
Duration: {event.duration} hours
Event Date & Time: {event.event_date.strftime('%B %d, %Y %I:%M %p')}
Ticket Price: {event.price}
Total Price: {event.price * quantity}

Promotion Details:
Bulk Discount: {event.bulk_discount_percent if event.bulk_discount_percent else 0}% (min tickets: {event.bulk_min_tickets if event.bulk_min_tickets else 'N/A'})
Free Ticket Offer: {event.free_tickets if event.free_tickets else 0} free ticket(s) (min tickets: {event.free_ticket_min if event.free_ticket_min else 'N/A'})

Your Ticket Details:
{ticket_details}

Thank you for your purchase!
"""
    mail.send(msg)
