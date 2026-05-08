"""Dashboard routes."""
from flask import Blueprint, render_template, session, redirect, url_for, jsonify
from app.models.test_session import TestSession
from app.models.report import BugReport
from app.database.db import get_db

dashboard_bp = Blueprint("dashboard", __name__)


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


@dashboard_bp.route("/dashboard")
@login_required
def index():
    stats        = TestSession.dashboard_stats()
    recent       = TestSession.recent(5)
    type_dist    = BugReport.type_distribution()
    sev_dist     = BugReport.severity_distribution()
    time_series  = TestSession.bugs_over_time()
    latest_metrics = get_db().execute(
        "SELECT * FROM model_metrics ORDER BY epoch DESC LIMIT 1"
    ).fetchone()

    return render_template(
        "dashboard/index.html",
        stats=stats,
        recent_sessions=recent,
        type_distribution=type_dist,
        severity_distribution=sev_dist,
        time_series=time_series,
        latest_metrics=latest_metrics,
    )


@dashboard_bp.route("/dashboard/overview")
@login_required
def overview():
    stats = TestSession.dashboard_stats()
    all_sessions = TestSession.all_sessions(50)
    return render_template("dashboard/overview.html", stats=stats,
                           sessions=all_sessions)


@dashboard_bp.route("/dashboard/model-metrics")
@login_required
def model_metrics():
    rows = get_db().execute(
        "SELECT * FROM model_metrics ORDER BY epoch ASC"
    ).fetchall()
    metrics = [dict(r) for r in rows]
    return render_template("dashboard/model_metrics.html", metrics=metrics)


@dashboard_bp.route("/dashboard/heatmap/<int:report_id>")
@login_required
def heatmap_view(report_id):
    report = get_db().execute(
        "SELECT * FROM bug_reports WHERE id=?", (report_id,)
    ).fetchone()
    return render_template("dashboard/heatmap_view.html", report=report)


@dashboard_bp.route("/api/stats")
@login_required
def api_stats():
    return jsonify(TestSession.dashboard_stats())
