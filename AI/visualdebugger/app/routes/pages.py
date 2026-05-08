"""Static pages: About, Contact, Home."""
from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.database.db import get_db

pages_bp = Blueprint("pages", __name__)

@pages_bp.route("/")
def home():
    return render_template("pages/home.html")

@pages_bp.route("/about")
def about():
    return render_template("pages/about.html")

@pages_bp.route("/comments", methods=["GET", "POST"])
def comments():
    db = get_db()
    if request.method == "POST":
        name    = request.form.get("name", "").strip()
        email   = request.form.get("email", "").strip()
        subject = request.form.get("subject", "").strip()
        message = request.form.get("message", "").strip()

        if not name or not email or not message:
            flash("Name, email, and message are required.", "error")
        else:
            db.execute(
                "INSERT INTO contacts (name, email, subject, message) VALUES (?, ?, ?, ?)",
                (name, email, subject, message),
            )
            db.commit()
            flash("Your comment has been posted! 🚀", "success")
            return redirect(url_for("pages.comments"))

    comments_data = db.execute("SELECT name, message, created_at FROM contacts ORDER BY created_at DESC").fetchall()
    return render_template("pages/comments.html", comments=comments_data)
