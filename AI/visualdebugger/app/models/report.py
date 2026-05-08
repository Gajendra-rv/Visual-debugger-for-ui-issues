"""Bug Report model."""
import json
from app.database.db import get_db


class BugReport:

    @staticmethod
    def create(session_id, bug_type, severity, confidence, description,
               bounding_box=None, screenshot_path=None, heatmap_path=None,
               screenshot_id=None):
        db = get_db()
        bbox_json = json.dumps(bounding_box) if bounding_box else None
        cur = db.execute(
            """INSERT INTO bug_reports
               (session_id, screenshot_id, bug_type, severity, confidence,
                bounding_box, screenshot_path, heatmap_path, description)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (session_id, screenshot_id, bug_type, severity, confidence,
             bbox_json, screenshot_path, heatmap_path, description),
        )
        db.commit()
        return cur.lastrowid

    @staticmethod
    def get_by_id(report_id):
        return get_db().execute(
            "SELECT * FROM bug_reports WHERE id=?", (report_id,)
        ).fetchone()

    @staticmethod
    def for_session(session_id):
        return get_db().execute(
            "SELECT * FROM bug_reports WHERE session_id=? ORDER BY created_at DESC",
            (session_id,),
        ).fetchall()

    @staticmethod
    def all_reports(limit=200, bug_type=None, severity=None):
        query = """SELECT br.*, ts.target_url, ts.user_id, u.username
                   FROM bug_reports br
                   JOIN test_sessions ts ON br.session_id = ts.id
                   JOIN users u ON ts.user_id = u.id
                   WHERE 1=1"""
        params = []
        if bug_type:
            query += " AND br.bug_type=?"; params.append(bug_type)
        if severity:
            query += " AND br.severity=?"; params.append(severity)
        query += " ORDER BY br.created_at DESC LIMIT ?"
        params.append(limit)
        return get_db().execute(query, params).fetchall()

    @staticmethod
    def type_distribution():
        rows = get_db().execute(
            "SELECT bug_type, COUNT(*) as cnt FROM bug_reports GROUP BY bug_type ORDER BY cnt DESC"
        ).fetchall()
        return [dict(r) for r in rows]

    @staticmethod
    def severity_distribution():
        rows = get_db().execute(
            "SELECT severity, COUNT(*) as cnt FROM bug_reports GROUP BY severity"
        ).fetchall()
        return [dict(r) for r in rows]

    @staticmethod
    def mark_false_positive(report_id):
        db = get_db()
        db.execute("UPDATE bug_reports SET is_false_positive=1 WHERE id=?", (report_id,))
        db.commit()
