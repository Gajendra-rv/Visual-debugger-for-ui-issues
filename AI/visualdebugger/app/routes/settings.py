"""Settings routes."""
from flask import (Blueprint, render_template, session, redirect,
                   url_for, request, flash)
from app.models.user import User

settings_bp = Blueprint("settings", __name__, url_prefix="/settings")


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


@settings_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    user = User.get_by_id(session["user_id"])
    errors = {}

    if request.method == "POST":
        action = request.form.get("action")

        if action == "profile":
            username = request.form.get("username", "").strip()
            bio      = request.form.get("bio", "").strip()
            if not username or len(username) < 3:
                errors["username"] = "Username must be at least 3 characters."
            else:
                user.update_profile(username=username, bio=bio)
                session["username"] = username
                flash("Profile updated successfully!", "success")
                return redirect(url_for("settings.index"))

        elif action == "password":
            current  = request.form.get("current_password", "")
            new_pwd  = request.form.get("new_password", "")
            confirm  = request.form.get("confirm_password", "")
            if not user.check_password(current):
                errors["current_password"] = "Incorrect current password."
            elif len(new_pwd) < 8:
                errors["new_password"] = "New password must be at least 8 characters."
            elif new_pwd != confirm:
                errors["confirm_password"] = "Passwords do not match."
            else:
                user.change_password(new_pwd)
                flash("Password changed successfully!", "success")
                return redirect(url_for("settings.index"))

    return render_template("settings/index.html", user=user, errors=errors)
