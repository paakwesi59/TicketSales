# routes/events.py
import os
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from extensions import db
from models.event import Event
from forms.forms import EventForm

events = Blueprint('events', __name__)

@events.route("/")
def home():
    upcoming_events = Event.query.filter(Event.event_date >= datetime.utcnow()).order_by(Event.event_date).all()
    return render_template("index.html", upcoming_events=upcoming_events)

@events.route("/events")
def list_events():
    events_list = Event.query.filter(Event.event_date >= datetime.utcnow()).order_by(Event.event_date).all()
    return render_template("events.html", events=events_list)

@events.route("/event/<int:event_id>")
def event_detail(event_id):
    event = Event.query.get_or_404(event_id)
    countdown = (event.event_date - datetime.utcnow()).total_seconds()
    return render_template("event_detail.html", event=event, countdown=countdown)

@events.route("/event/new", methods=["GET", "POST"])
@login_required
def new_event():
    if current_user.user_type != "event_organizer":
        flash("Only event organizers can create events.", "danger")
        return redirect(url_for("events.list_events"))
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
        if form.image.data and hasattr(form.image.data, "filename") and form.image.data.filename:
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
        return redirect(url_for("events.list_events"))
    return render_template("new_event.html", form=form)

@events.route("/event/<int:event_id>/edit", methods=["GET", "POST"])
@login_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    if current_user.id != event.created_by:
        flash("You are not authorized to edit this event.", "danger")
        return redirect(url_for("events.list_events"))
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

        if form.image.data and hasattr(form.image.data, "filename") and form.image.data.filename:
            file = form.image.data
            filename = secure_filename(file.filename)
            upload_path = os.path.join(current_app.root_path, 'static', 'event_images')
            os.makedirs(upload_path, exist_ok=True)
            file_path = os.path.join(upload_path, filename)
            file.save(file_path)
            event.image = filename

        db.session.commit()
        flash("Event updated successfully!", "success")
        return redirect(url_for("events.event_detail", event_id=event.id))
    return render_template("edit_event.html", form=form, event=event)

@events.route("/event/<int:event_id>/delete", methods=["POST"])
@login_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    if current_user.id != event.created_by:
        flash("You are not authorized to delete this event.", "danger")
        return redirect(url_for("events.list_events"))
    db.session.delete(event)
    db.session.commit()
    flash("Event deleted successfully.", "success")
    return redirect(url_for("events.dashboard"))

@events.route("/dashboard")
@login_required
def dashboard():
    if current_user.user_type == "event_organizer":
        events_list = Event.query.filter_by(created_by=current_user.id).all()
        events_data = []
        total_actual_revenue = 0
        total_lost_revenue = 0
        for event in events_list:
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
