# routes/main.py
import os
import uuid
import qrcode
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, send_file
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename

# Import extensions and models from our app and packages
from app import db, bcrypt
from models.user import User
from models.event import Event
from models.ticket import Ticket
from forms.forms import (
    RegistrationForm,
    LoginForm,
    ForgotPasswordForm,
    ResetPasswordForm,
    EventForm,
    TicketPurchaseForm
)

# Import service functions
from services.email_service import send_confirmation_email, send_reset_email, send_ticket_email
from services.ticket_service import process_ticket_purchase

main = Blueprint('main', __name__)

@main.route("/")
def home():
    upcoming_events = Event.query.filter(Event.event_date >= datetime.utcnow()).order_by(Event.event_date).all()
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    return render_template("index.html", upcoming_events=upcoming_events)

@main.route("/events")
def events():
    events = Event.query.filter(Event.event_date >= datetime.utcnow()).order_by(Event.event_date).all()
    return render_template("events.html", events=events)

@main.route("/event/new", methods=["GET", "POST"])
@login_required
def new_event():
    if current_user.user_type != "event_organizer":
        flash("Only event organizers can create events.", "danger")
        return redirect(url_for("main.dashboard"))
    form = EventForm()
    if form.validate_on_submit():
        event = Event(
            title=form.title.data,
            description=form.description.data,
            event_date=form.event_date.data,
            price=form.price.data,
            total_tickets=form.total_tickets.data,
            venue=form.venue.data,
            duration=form.duration.data,
            created_by=current_user.id,
            bulk_min_tickets=form.bulk_min_tickets.data,
            bulk_discount_percent=form.bulk_discount_percent.data,
            free_ticket_min=form.free_ticket_min.data,
            free_tickets=form.free_tickets.data
        )
        if form.image.data:
            file = form.image.data
            filename = secure_filename(file.filename)
            upload_path = os.path.join(current_app.root_path, 'static', 'event_images')
            os.makedirs(upload_path, exist_ok=True)
            file_path = os.path.join(upload_path, filename)
            file.save(file_path)
            event.image = filename
        db.session.add(event)
        db.session.commit()
        flash("Event created successfully!", "success")
        return redirect(url_for("main.events"))
    return render_template("new_event.html", form=form)

@main.route("/event/<int:event_id>/edit", methods=["GET", "POST"])
@login_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    if current_user.id != event.created_by:
        flash("You are not authorized to edit this event.", "danger")
        return redirect(url_for("main.events"))
    form = EventForm(obj=event)
    if form.validate_on_submit():
        event.title = form.title.data
        event.description = form.description.data
        event.event_date = form.event_date.data
        event.price = form.price.data
        event.total_tickets = form.total_tickets.data
        event.venue = form.venue.data
        event.duration = form.duration.data
        event.bulk_min_tickets = form.bulk_min_tickets.data
        event.bulk_discount_percent = form.bulk_discount_percent.data
        event.free_ticket_min = form.free_ticket_min.data
        event.free_tickets = form.free_tickets.data
        if form.image.data:
            file = form.image.data
            filename = secure_filename(file.filename)
            upload_path = os.path.join(current_app.root_path, 'static', 'event_images')
            os.makedirs(upload_path, exist_ok=True)
            file_path = os.path.join(upload_path, filename)
            file.save(file_path)
            event.image = filename
        db.session.commit()
        flash("Event updated successfully!", "success")
        return redirect(url_for("main.event_detail", event_id=event.id))
    return render_template("edit_event.html", form=form, event=event)

@main.route("/event/<int:event_id>/delete", methods=["POST"])
@login_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    if current_user.id != event.created_by:
        flash("You are not authorized to delete this event.", "danger")
        return redirect(url_for("main.events"))
    db.session.delete(event)
    db.session.commit()
    flash("Event deleted successfully.", "success")
    return redirect(url_for("main.dashboard"))

@main.route("/event/<int:event_id>")
def event_detail(event_id):
    event = Event.query.get_or_404(event_id)
    countdown = (event.event_date - datetime.utcnow()).total_seconds()
    return render_template("event_detail.html", event=event, countdown=countdown)

@main.route("/event/<int:event_id>/buy", methods=["GET", "POST"])
def buy_ticket(event_id):
    event = Event.query.get_or_404(event_id)
    form = TicketPurchaseForm()
    if form.validate_on_submit():
        quantity = form.quantity.data

        # Calculate the base total price and promotion details (for checkout view)
        total_price = event.price * quantity
        discount = 0.0
        free_tickets = 0

        if event.bulk_min_tickets and event.bulk_discount_percent:
            if quantity >= event.bulk_min_tickets:
                discount = (event.bulk_discount_percent / 100.0) * total_price

        if event.free_ticket_min and event.free_tickets:
            if quantity >= event.free_ticket_min:
                free_tickets = event.free_tickets

        final_price = total_price - discount

        return render_template(
            "checkout.html",
            event=event,
            email=form.email.data,
            quantity=quantity,
            total_price=total_price,
            discount=discount,
            free_tickets=free_tickets,
            final_price=final_price
        )
    return render_template("buy_ticket.html", form=form, event=event)

@main.route("/checkout/confirm/<int:event_id>", methods=["POST"])
def confirm_purchase(event_id):
    event = Event.query.get_or_404(event_id)
    email = request.form.get("email")
    try:
        quantity = int(request.form.get("quantity"))
    except (ValueError, TypeError):
        flash("Invalid quantity.", "danger")
        return redirect(url_for("main.buy_ticket", event_id=event.id))

    # Process ticket purchase via the ticket service
    result = process_ticket_purchase(event, email, quantity)
    if not result.get("success"):
        flash(result.get("message", "Ticket purchase failed."), "danger")
        return redirect(url_for("main.buy_ticket", event_id=event.id))

    tickets_generated = result.get("tickets")
    discount = result.get("discount", 0.0)
    free_tickets = result.get("free_tickets", 0)
    final_price = result.get("final_price", 0.0)

    try:
        send_ticket_email(email, event, quantity, tickets_generated)
    except Exception as e:
        current_app.logger.error(f"Error sending ticket email: {e}")
        flash("Tickets purchased successfully, but there was an error sending the ticket confirmation email.", "danger")
    else:
        flash(f"Tickets purchased successfully! You received {free_tickets} free ticket(s). Total Price: GHC{final_price:.2f}. Check your email for details.", "success")

    return render_template("purchase_confirmation.html", event=event, tickets=tickets_generated,
                           quantity=quantity, discount=discount, free_tickets=free_tickets, final_price=final_price)

@main.route("/ticket/<int:ticket_id>/download")
def download_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    file_path = os.path.join(current_app.root_path, 'static', 'tickets_qr', ticket.qr_code_filename)
    return send_file(file_path, as_attachment=True, download_name=ticket.qr_code_filename)

@main.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash("Email already registered. Please use a different email.", "danger")
            return redirect(url_for("main.register"))
        if User.query.filter_by(username=form.username.data).first():
            flash("Username already taken. Please choose another.", "danger")
            return redirect(url_for("main.register"))
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_password,
            user_type=form.user_type.data,
            confirmed=False
        )
        db.session.add(new_user)
        db.session.commit()
        send_confirmation_email(new_user)
        flash("Account created! Please check your email to confirm your account.", "success")
        return redirect(url_for("main.login"))
    return render_template("register.html", form=form)

@main.route("/confirm/<token>")
def confirm_email(token):
    email = User.confirm_token(token)
    if not email:
        flash("The confirmation link is invalid or has expired.", "danger")
        return redirect(url_for("main.login"))
    user = User.query.filter_by(email=email).first_or_404()
    if user.confirmed:
        flash("Account already confirmed. Please log in.", "info")
    else:
        user.confirmed = True
        db.session.commit()
        flash("Your account has been confirmed! You can now log in.", "success")
    return redirect(url_for("main.login"))

@main.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            if not user.confirmed:
                flash("Please confirm your email before logging in.", "warning")
                return redirect(url_for("main.login"))
            login_user(user)
            flash("Login successful!", "success")
            next_page = request.args.get("next")
            return redirect(next_page if next_page else url_for("main.dashboard"))
        else:
            flash("Invalid email or password.", "danger")
    return render_template("login.html", form=form)

@main.route("/dashboard")
@login_required
def dashboard():
    if current_user.user_type == "event_organizer":
        events = Event.query.filter_by(created_by=current_user.id).all()
        events_data = []
        total_actual_revenue = 0
        total_lost_revenue = 0
        for event in events:
            actual_revenue = event.tickets_sold * event.price
            potential_revenue = event.total_tickets * event.price
            lost_revenue = potential_revenue - actual_revenue
            tickets_remaining = event.total_tickets - event.tickets_sold
            total_actual_revenue += actual_revenue
            total_lost_revenue += lost_revenue
            events_data.append({
                "id": event.id,
                "title": event.title,
                "event_date": event.event_date,
                "total_tickets": event.total_tickets,
                "tickets_sold": event.tickets_sold,
                "tickets_remaining": tickets_remaining,
                "actual_revenue": actual_revenue,
                "lost_revenue": lost_revenue
            })
        return render_template("dashboard.html",
                               events_data=events_data,
                               total_actual_revenue=total_actual_revenue,
                               total_lost_revenue=total_lost_revenue)
    else:
        return render_template("dashboard.html")

@main.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.login"))

@main.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_reset_email(user)
            flash("A password reset link has been sent to your email.", "info")
        else:
            flash("Email not found. Please check and try again.", "danger")
        return redirect(url_for("main.login"))
    return render_template("forgot_password.html", form=form)

@main.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    form = ResetPasswordForm()
    if form.validate_on_submit():
        email = User.verify_reset_token(token)
        if not email:
            flash("The reset link is invalid or has expired.", "danger")
            return redirect(url_for("main.forgot_password"))
        user = User.query.filter_by(email=email).first_or_404()
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user.password = hashed_password
        db.session.commit()
        flash("Your password has been updated!", "success")
        return redirect(url_for("main.login"))
    return render_template("reset_password.html", form=form)
