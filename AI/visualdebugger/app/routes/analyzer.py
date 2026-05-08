"""Analyzer routes — run CNN bug detection on a URL."""
import os, json, threading, uuid
from flask import (Blueprint, render_template, request, redirect,
                   url_for, session, jsonify, current_app, flash)
from app.models.test_session import TestSession
from app.models.report import BugReport
from app.services.bug_detector import BugDetector

analyzer_bp = Blueprint("analyzer", __name__, url_prefix="/analyzer")

_session_progress = {}   # session_id -> progress dict


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


from werkzeug.utils import secure_filename

@analyzer_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        target_url   = request.form.get("target_url", "").strip()
        session_name = request.form.get("session_name", "").strip() or None

        if not target_url.startswith(("http://", "https://")):
            flash("Please enter a valid URL starting with http:// or https://", "error")
            return redirect(url_for("analyzer.index"))

        user_id    = session["user_id"]
        session_id = TestSession.create(user_id, target_url, session_name)

        # Run analysis in background thread
        _session_progress[session_id] = {"status": "running", "step": "Starting…", "percent": 0}
        t = threading.Thread(
            target=_run_analysis,
            args=(current_app._get_current_object(), session_id, target_url),
            daemon=True,
        )
        t.start()
        return redirect(url_for("analyzer.progress", session_id=session_id))

    return render_template("analyzer/index.html")


@analyzer_bp.route("/manual", methods=["GET", "POST"])
@login_required
def manual():
    if request.method == "POST":
        if "file" not in request.files:
            flash("No file part", "error")
            return redirect(request.url)
        
        file = request.files["file"]
        if file.filename == "":
            flash("No selected file", "error")
            return redirect(request.url)
            
        if file:
            # Prefix filename with unique ID to avoid collisions and invalid names
            unique_id = uuid.uuid4().hex[:8]
            filename = secure_filename(file.filename)
            if not filename or filename.startswith('.'):
                filename = f"upload_{unique_id}.png"
            else:
                filename = f"{unique_id}_{filename}"

            upload_path = os.path.abspath(os.path.join(current_app.config["UPLOAD_FOLDER"], filename))
            file.save(upload_path)
            
            session_name = request.form.get("session_name", "").strip() or "Manual Upload"
            target_url = f"manual://{filename}"
            user_id = session["user_id"]
            
            session_id = TestSession.create(user_id, target_url, session_name)
            
            _session_progress[session_id] = {"status": "running", "step": "Preprocessing uploaded image…", "percent": 0}
            t = threading.Thread(
                target=_run_manual_analysis,
                args=(current_app._get_current_object(), session_id, upload_path),
                daemon=True,
            )
            t.start()
            return redirect(url_for("analyzer.progress", session_id=session_id))
            
    return render_template("analyzer/manual.html")

def _run_manual_analysis(app, session_id, upload_path):
    with app.app_context():
        try:
            detector = BugDetector(app.config)

            _session_progress[session_id] = {"status": "running", "step": "Preprocessing image…", "percent": 35}
            processed = detector.preprocess(upload_path)

            _session_progress[session_id] = {"status": "running", "step": "Running CNN inference…", "percent": 60}
            predictions = detector.predict(processed, upload_path, session_id)

            _session_progress[session_id] = {"status": "running", "step": "Generating heatmaps…", "percent": 80}
            for pred in predictions:
                BugReport.create(
                    session_id     = session_id,
                    bug_type       = pred["bug_type"],
                    severity       = pred["severity"],
                    confidence     = pred["confidence"],
                    description    = pred["description"],
                    bounding_box   = pred.get("bbox"),
                    screenshot_path= pred.get("screenshot_path"),
                    heatmap_path   = pred.get("heatmap_path"),
                )

            TestSession.update_status(
                session_id, "completed",
                bugs_found=len(predictions),
                accuracy=detector.session_accuracy,
            )
            _session_progress[session_id] = {
                "status": "completed", "step": "Done!", "percent": 100,
                "redirect": f"/analyzer/result/{session_id}",
            }
        except Exception as e:
            app.logger.exception("Analysis failed for manual session %s", session_id)
            TestSession.update_status(session_id, "failed")
            _session_progress[session_id] = {
                "status": "failed", "step": str(e), "percent": 0
            }


@analyzer_bp.route("/progress/<int:session_id>")
@login_required
def progress(session_id):
    sess = TestSession.get_by_id(session_id)
    return render_template("analyzer/progress.html", test_session=sess)


@analyzer_bp.route("/api/progress/<int:session_id>")
@login_required
def api_progress(session_id):
    prog = _session_progress.get(session_id, {"status": "unknown", "percent": 0})
    return jsonify(prog)


@analyzer_bp.route("/result/<int:session_id>")
@login_required
def result(session_id):
    sess  = TestSession.get_by_id(session_id)
    bugs  = BugReport.for_session(session_id)
    return render_template("analyzer/result.html", test_session=sess, bugs=bugs)


def _run_analysis(app, session_id, target_url):
    with app.app_context():
        try:
            detector = BugDetector(app.config)

            _session_progress[session_id] = {"status": "running", "step": "Capturing screenshot…", "percent": 15}
            screenshot_path = detector.capture_screenshot(target_url, session_id)

            _session_progress[session_id] = {"status": "running", "step": "Preprocessing image…", "percent": 35}
            processed = detector.preprocess(screenshot_path)

            _session_progress[session_id] = {"status": "running", "step": "Running CNN inference…", "percent": 60}
            predictions = detector.predict(processed, screenshot_path, session_id)

            _session_progress[session_id] = {"status": "running", "step": "Generating heatmaps…", "percent": 80}
            for pred in predictions:
                BugReport.create(
                    session_id     = session_id,
                    bug_type       = pred["bug_type"],
                    severity       = pred["severity"],
                    confidence     = pred["confidence"],
                    description    = pred["description"],
                    bounding_box   = pred.get("bbox"),
                    screenshot_path= pred.get("screenshot_path"),
                    heatmap_path   = pred.get("heatmap_path"),
                )

            TestSession.update_status(
                session_id, "completed",
                bugs_found=len(predictions),
                accuracy=detector.session_accuracy,
            )
            _session_progress[session_id] = {
                "status": "completed", "step": "Done!", "percent": 100,
                "redirect": f"/analyzer/result/{session_id}",
            }
        except Exception as e:
            app.logger.exception("Analysis failed for session %s", session_id)
            TestSession.update_status(session_id, "failed")
            _session_progress[session_id] = {
                "status": "failed", "step": str(e), "percent": 0
            }
