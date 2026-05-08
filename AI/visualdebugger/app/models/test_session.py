"""Test Session model."""
import json
from app.database.db import get_db


class TestSession:

    @staticmethod
    def create(user_id, target_url, session_name=None):
        db = get_db()
        cur = db.execute(
            """INSERT INTO test_sessions (user_id, target_url, session_name, status, start_time)
               VALUES (?, ?, ?, 'running', CURRENT_TIMESTAMP)""",
            (user_id, target_url, session_name or f"Session for {target_url[:40]}"),
        )
        db.commit()
        return cur.lastrowid

    @staticmethod
    def get_by_id(session_id):
        return get_db().execute(
            """SELECT ts.*, u.username FROM test_sessions ts
               JOIN users u ON ts.user_id = u.id
               WHERE ts.id = ?""",
            (session_id,),
        ).fetchone()

    @staticmethod
    def all_for_user(user_id, limit=50):
        return get_db().execute(
            "SELECT * FROM test_sessions WHERE user_id=? ORDER BY created_at DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()

    @staticmethod
    def all_sessions(limit=100):
        return get_db().execute(
            """SELECT ts.*, u.username FROM test_sessions ts
               JOIN users u ON ts.user_id = u.id
               ORDER BY ts.created_at DESC LIMIT ?""",
            (limit,),
        ).fetchall()

    @staticmethod
    def update_status(session_id, status, bugs_found=None, accuracy=None):
        db = get_db()
        end_clause = ", end_time=CURRENT_TIMESTAMP" if status in ("completed", "failed") else ""
        bugs_part  = f", bugs_found={int(bugs_found)}"  if bugs_found is not None else ""
        acc_part   = f", accuracy={float(accuracy)}"     if accuracy  is not None else ""
        db.execute(
            f"UPDATE test_sessions SET status=?{bugs_part}{acc_part}{end_clause} WHERE id=?",
            (status, session_id),
        )
        db.commit()

    @staticmethod
    def dashboard_stats():
        db = get_db()
        total    = db.execute("SELECT COUNT(*) FROM test_sessions").fetchone()[0]
        bugs     = db.execute("SELECT SUM(bugs_found) FROM test_sessions").fetchone()[0] or 0
        avg_acc  = db.execute(
            "SELECT AVG(accuracy) FROM test_sessions WHERE accuracy IS NOT NULL"
        ).fetchone()[0] or 0
        active   = db.execute(
            "SELECT COUNT(*) FROM test_sessions WHERE status='running'"
        ).fetchone()[0]
        return {
            "total_sessions": total,
            "bugs_found": int(bugs),
            "avg_accuracy": round(avg_acc * 100, 1),
            "active_tests": active,
        }

    @staticmethod
    def recent(limit=5):
        return get_db().execute(
            """SELECT ts.*, u.username FROM test_sessions ts
               JOIN users u ON ts.user_id = u.id
               ORDER BY ts.created_at DESC LIMIT ?""",
            (limit,),
        ).fetchall()

    @staticmethod
    def bugs_over_time():
        """Returns (date, count) tuples for chart."""
        rows = get_db().execute(
            """SELECT DATE(created_at) as d, SUM(bugs_found) as c
               FROM test_sessions
               WHERE created_at >= DATE('now', '-30 days')
               GROUP BY d ORDER BY d""",
        ).fetchall()
        return [dict(r) for r in rows]
