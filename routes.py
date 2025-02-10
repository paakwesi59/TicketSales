import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from flask_mail import Message
from datetime import datetime
from app import db, bcrypt, mail
from models import User, Event
from forms import RegistrationForm, LoginForm, ForgotPasswordForm, ResetPasswordForm, EventForm

main = Blueprint('main', __name__)

def send_confirmation_email(user):
    token = user.generate_confirmation_token()
    confirm_url = url_for("main.confirm_email", token=token, _external=True)
    subject = "Please confirm your email"
    msg = Message(subject, sender=current_app.config["MAIL_DEFAULT_SENDER"], recipients=[user.email])
    msg.body = f"Hello {user.username},\n\nPlease confirm your email by clicking the following link:\n{confirm_url}\n\nThank you!"
    mail.send(msg)

def send_reset_email(user):
    token = user.generate_reset_token()
    reset_url = url_for("main.reset_password", token=token, _external=True)
    subject = "Password Reset Request"
    msg = Message(subject, sender=current_app.config["MAIL_DEFAULT_SENDER"], recipients=[user.email])
    msg.body = f"Hello {user.username},\n\nTo reset your password, please click the link below:\n{reset_url}\n\nIf you did not request a password reset, please ignore this email."
    mail.send(msg)

@main.route("/")
def home():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    return render_template("index.html")

@main.route("/events")
def events():
    events = Event.query.filter(Event.event_date >= datetime.utcnow()).order_by(Event.event_date).all()
    return render_template("events.html", events=events)

@main.route("/event/new", methods=["GET", "POST"])
@login_required
def new_event():
    # Only event organizers can create events.
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
            created_by=current_user.id
        )
        # Handle image upload
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

@main.route("/event/<int:event_id>")
def event_detail(event_id):
    event = Event.query.get_or_404(event_id)
    countdown = (event.event_date - datetime.utcnow()).total_seconds()
    return render_template("event_detail.html", event=event, countdown=countdown)

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
