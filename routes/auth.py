# routes/auth.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, current_user
from extensions import db, bcrypt
from models.user import User
from forms.forms import RegistrationForm, LoginForm, ForgotPasswordForm, ResetPasswordForm
from services.email_service import send_confirmation_email, send_reset_email

auth = Blueprint('auth', __name__, url_prefix='/auth')

@auth.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("events.dashboard"))
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash("Email already registered. Please use a different email.", "danger")
            return redirect(url_for("auth.register"))
        if User.query.filter_by(username=form.username.data).first():
            flash("Username already taken. Please choose another.", "danger")
            return redirect(url_for("auth.register"))
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
        return redirect(url_for("auth.login"))
    return render_template("register.html", form=form)

@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("events.dashboard"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            if not user.confirmed:
                flash("Please confirm your email before logging in.", "warning")
                return redirect(url_for("auth.login"))
            login_user(user)
            flash("Login successful!", "success")
            next_page = request.args.get("next")
            return redirect(next_page if next_page else url_for("events.dashboard"))
        else:
            flash("Invalid email or password.", "danger")
    return render_template("login.html", form=form)

@auth.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))

@auth.route("/confirm/<token>")
def confirm_email(token):
    email = User.confirm_token(token)
    if not email:
        flash("The confirmation link is invalid or has expired.", "danger")
        return redirect(url_for("auth.login"))
    user = User.query.filter_by(email=email).first_or_404()
    if user.confirmed:
        flash("Account already confirmed. Please log in.", "info")
    else:
        user.confirmed = True
        db.session.commit()
        flash("Your account has been confirmed! You can now log in.", "success")
    return redirect(url_for("auth.login"))

@auth.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_reset_email(user)
            flash("A password reset link has been sent to your email.", "info")
        else:
            flash("Email not found. Please check and try again.", "danger")
        return redirect(url_for("auth.login"))
    return render_template("forgot_password.html", form=form)

@auth.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    form = ResetPasswordForm()
    if form.validate_on_submit():
        email = User.verify_reset_token(token)
        if not email:
            flash("The reset link is invalid or has expired.", "danger")
            return redirect(url_for("auth.forgot_password"))
        user = User.query.filter_by(email=email).first_or_404()
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user.password = hashed_password
        db.session.commit()
        flash("Your password has been updated!", "success")
        return redirect(url_for("auth.login"))
    return render_template("reset_password.html", form=form)
