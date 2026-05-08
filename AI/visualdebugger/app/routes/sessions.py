"""Sessions routes."""
from flask import Blueprint, render_template, session, redirect, url_for
from app.models.test_session import TestSession
from app.models.report import BugReport

sessions_bp = Blueprint("sessions", __name__, url_prefix="/sessions")


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


@sessions_bp.route("/")
@login_required
def index():
    all_sess = TestSession.all_sessions(100)
    return render_template("sessions/index.html", sessions=all_sess)


@sessions_bp.route("/<int:session_id>")
@login_required
def detail(session_id):
    sess = TestSession.get_by_id(session_id)
    if not sess:
        return redirect(url_for("sessions.index"))
    bugs = BugReport.for_session(session_id)
    return render_template("sessions/detail.html", test_session=sess, bugs=bugs)
