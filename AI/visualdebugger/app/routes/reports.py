"""Reports routes."""
from flask import Blueprint, render_template, session, redirect, url_for, request, send_file, flash
from app.models.report import BugReport
from app.models.test_session import TestSession

reports_bp = Blueprint("reports", __name__, url_prefix="/reports")


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


@reports_bp.route("/")
@login_required
def index():
    bug_type = request.args.get("type")
    severity = request.args.get("severity")
    reports  = BugReport.all_reports(limit=200, bug_type=bug_type, severity=severity)
    return render_template("reports/index.html", reports=reports,
                           filter_type=bug_type, filter_severity=severity)


@reports_bp.route("/<int:report_id>")
@login_required
def detail(report_id):
    report = BugReport.get_by_id(report_id)
    if not report:
        return redirect(url_for("reports.index"))
    return render_template("reports/detail.html", report=report)


@reports_bp.route("/<int:report_id>/false-positive", methods=["POST"])
@login_required
def mark_false_positive(report_id):
    BugReport.mark_false_positive(report_id)
    flash("Marked as false positive.", "info")
    return redirect(url_for("reports.detail", report_id=report_id))


@reports_bp.route("/export/pdf/<int:session_id>")
@login_required
def export_pdf(session_id):
    from app.services.report_generator import generate_pdf
    pdf_path = generate_pdf(session_id)
    return send_file(pdf_path, as_attachment=True,
                     download_name=f"report_session_{session_id}.pdf")
