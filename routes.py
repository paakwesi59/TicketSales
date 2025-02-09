#
# from flask import Blueprint, render_template, redirect, url_for, flash, request
# from flask_login import login_user, logout_user, login_required, current_user
# from app import db, bcrypt
# from models import User
# from forms import RegistrationForm, LoginForm
#
# # Create the blueprint named 'main'
# main = Blueprint('main', __name__)
#
# @main.route("/")
# def home():
#     # If a user is logged in, send them to the dashboard; otherwise show the index page.
#     if current_user.is_authenticated:
#         return redirect(url_for('main.dashboard'))
#     return render_template('index.html')
#
# @main.route("/register", methods=["GET", "POST"])
# def register():
#     if current_user.is_authenticated:
#         return redirect(url_for('main.dashboard'))
#     form = RegistrationForm()
#     if form.validate_on_submit():
#         # Check if the email already exists
#         existing_user = User.query.filter_by(email=form.email.data).first()
#         if existing_user:
#             flash("Email already registered. Please use a different email.", "danger")
#             return redirect(url_for('main.register'))
#
#         # Check if the username already exists
#         existing_username = User.query.filter_by(username=form.username.data).first()
#         if existing_username:
#             flash("Username already taken. Please choose another one.", "danger")
#             return redirect(url_for('main.register'))
#
#         # Hash the password and create a new user
#         hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
#         new_user = User(
#             username=form.username.data,
#             email=form.email.data,
#             password=hashed_password,
#             user_type=form.user_type.data
#         )
#         db.session.add(new_user)
#         db.session.commit()
#
#         flash("Account created successfully! You can now log in.", "success")
#         return redirect(url_for('main.login'))
#     return render_template('register.html', form=form)
#
# @main.route("/login", methods=["GET", "POST"])
# def login():
#     if current_user.is_authenticated:
#         return redirect(url_for('main.dashboard'))
#     form = LoginForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(email=form.email.data).first()
#         if user and bcrypt.check_password_hash(user.password, form.password.data):
#             login_user(user)
#             flash("Login successful!", "success")
#             next_page = request.args.get('next')
#             return redirect(next_page if next_page else url_for('main.dashboard'))
#         else:
#             flash("Invalid email or password.", "danger")
#     return render_template('login.html', form=form)
#
# @main.route("/dashboard")
# @login_required
# def dashboard():
#     return render_template('dashboard.html')
#
# @main.route("/logout")
# @login_required
# def logout():
#     logout_user()
#     flash("You have been logged out.", "info")
#     return redirect(url_for('main.login'))
#
# # Stub route for events page (used by the index page hero button)
# @main.route("/events")
# def events():
#     return render_template("events.html")


from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message
from app import db, bcrypt, mail
from models import User
from forms import RegistrationForm, LoginForm, ForgotPasswordForm, ResetPasswordForm

main = Blueprint('main', __name__)


def send_reset_email(user):
    """Send a password reset email to the given user."""
    token = user.generate_reset_token()
    reset_url = url_for('main.reset_password', token=token, _external=True)
    subject = "Password Reset Request"
    sender = current_app.config["MAIL_DEFAULT_SENDER"]
    recipients = [user.email]
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = f"""Hello {user.username},

To reset your password, please click on the following link:
{reset_url}

If you did not request a password reset, please ignore this email.
"""
    mail.send(msg)


@main.route("/")
def home():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    return render_template("index.html")


@main.route("/events")
def events():
    return render_template("events.html")


@main.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if email or username already exists
        if User.query.filter_by(email=form.email.data).first():
            flash("Email already registered. Please use a different email.", "danger")
            return redirect(url_for("main.register"))
        if User.query.filter_by(username=form.username.data).first():
            flash("Username already taken. Please choose another.", "danger")
            return redirect(url_for("main.register"))

        # Hash the password and create a new user
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

        # Optionally, send an email confirmation here if you implement that feature.
        # For now, we focus on sending the reset password email in the forgot-password flow.

        flash("Account created successfully! Please check your email to confirm your account.", "success")
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
