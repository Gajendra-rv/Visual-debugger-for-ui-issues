"""Authentication routes: login, signup, logout."""
import re
from flask import (Blueprint, render_template, redirect, url_for,
                   flash, request, session)
from werkzeug.security import check_password_hash
from app.models.user import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

EMAIL_RE = re.compile(r"^[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}$")


def _logged_in():
    return "user_id" in session


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if _logged_in():
        return redirect(url_for("pages.home"))

    error = None
    if request.method == "POST":
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            error = "Both fields are required."
        else:
            user = User.get_by_email(email)
            if user and user.check_password(password):
                session.clear()
                session["user_id"]   = user.id
                session["username"]  = user.username
                session["role"]      = user.role
                session.permanent    = True
                flash("Welcome back, " + user.username + "! 🎉", "success")
                return redirect(url_for("pages.home"))
            else:
                error = "Invalid email or password."

    return render_template("auth/login.html", error=error)


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if _logged_in():
        return redirect(url_for("pages.home"))

    errors = {}
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm  = request.form.get("confirm_password", "")

        if not username or len(username) < 3:
            errors["username"] = "Username must be at least 3 characters."
        if not EMAIL_RE.match(email):
            errors["email"] = "Enter a valid email address."
        if len(password) < 8:
            errors["password"] = "Password must be at least 8 characters."
        if password != confirm:
            errors["confirm_password"] = "Passwords do not match."
        if not errors:
            if User.get_by_email(email):
                errors["email"] = "Email already registered."
            if User.get_by_username(username):
                errors["username"] = "Username already taken."

        if not errors:
            User.create(username, email, password)
            flash("Account created! Please log in.", "success")
            return redirect(url_for("auth.login"))

    return render_template("auth/signup.html", errors=errors,
                           form=request.form)


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
