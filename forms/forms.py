# forms/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField, TextAreaField, FloatField, IntegerField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional
from wtforms.fields import DateTimeLocalField
from flask_wtf.file import FileField, FileAllowed

class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField("Confirm Password",
                                     validators=[DataRequired(), EqualTo('password', message='Passwords must match.')])
    user_type = SelectField("User Type", choices=[("event_organizer", "Event Organizer")], validators=[DataRequired()])
    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class ForgotPasswordForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Reset Password")

class ResetPasswordForm(FlaskForm):
    password = PasswordField("New Password", validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField("Confirm New Password",
                                     validators=[DataRequired(), EqualTo('password', message='Passwords must match.')])
    submit = SubmitField("Change Password")

class EventForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=150)])
    description = TextAreaField("Description", validators=[DataRequired()])
    event_date = DateTimeLocalField("Event Date & Time", format="%Y-%m-%dT%H:%M", validators=[DataRequired()])
    price = FloatField("Ticket Price", validators=[DataRequired()])
    total_tickets = IntegerField("Total Tickets", validators=[DataRequired()])
    venue = StringField("Venue", validators=[DataRequired(), Length(max=150)])
    duration = FloatField("Duration (hours)", validators=[DataRequired()])
    image = FileField("Event Image", validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'], "Images only!")])
    bulk_min_tickets = IntegerField("Minimum Tickets for Bulk Discount", validators=[Optional()])
    bulk_discount_percent = FloatField("Bulk Discount (%)", validators=[Optional()])
    free_ticket_min = IntegerField("Minimum Tickets for Free Ticket Offer", validators=[Optional()])
    free_tickets = IntegerField("Number of Free Tickets", validators=[Optional()])
    submit = SubmitField("Submit")

class TicketPurchaseForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    quantity = IntegerField("Quantity", validators=[DataRequired()])
    submit = SubmitField("Proceed to Checkout")
