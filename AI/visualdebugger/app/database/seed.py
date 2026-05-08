"""Seed the database with demo/sample data."""
import json
import random
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from app.database.db import get_db


BUG_TYPES = ["layout", "color", "overlap", "missing", "alignment", "contrast"]
SEVERITIES = ["low", "medium", "high", "critical"]
STATUSES = ["pending", "running", "completed", "failed"]

DEMO_URLS = [
    "https://example.com",
    "https://google.com",
    "https://github.com",
    "https://stackoverflow.com",
    "https://wikipedia.org",
]

DESCRIPTIONS = {
    "layout": "Elements are incorrectly positioned relative to their container.",
    "color":  "Color contrast ratio is below WCAG AA standard (4.5:1).",
    "overlap": "Two or more UI components are overlapping unexpectedly.",
    "missing": "Expected UI element not rendered in the viewport.",
    "alignment": "Element is misaligned with its grid baseline.",
    "contrast": "Background-foreground contrast is insufficient for readability.",
}


def seed_all():
    db = get_db()

    # ── Users ──────────────────────────────────────────────────────────────────
    users = [
        ("admin",   "admin@debugger.ai",   generate_password_hash("Admin@123"),   "admin"),
        ("dhanush", "dhanush@debugger.ai",  generate_password_hash("Dhanush@123"), "user"),
        ("guest",   "guest@debugger.ai",    generate_password_hash("Guest@123"),   "user"),
    ]
    for username, email, pw_hash, role in users:
        db.execute(
            "INSERT OR IGNORE INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
            (username, email, pw_hash, role),
        )
    db.commit()

    user_ids = [row["id"] for row in db.execute("SELECT id FROM users").fetchall()]

    # ── Test Sessions + Screenshots + Bug Reports ──────────────────────────────
    now = datetime.utcnow()
    for i in range(15):
        uid = random.choice(user_ids)
        url = random.choice(DEMO_URLS)
        status = random.choice(["completed", "completed", "completed", "failed"])
        start = now - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))
        end   = start + timedelta(minutes=random.randint(1, 10))
        bugs_found = random.randint(0, 8)
        accuracy   = round(random.uniform(0.78, 0.98), 4)

        cur = db.execute(
            """INSERT INTO test_sessions
               (user_id, session_name, target_url, status, bugs_found, accuracy, start_time, end_time)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (uid, f"Session #{i+1}", url, status, bugs_found, accuracy,
             start.isoformat(), end.isoformat()),
        )
        session_id = cur.lastrowid

        # Screenshot stub
        shot_cur = db.execute(
            "INSERT INTO screenshots (session_id, file_path, width, height) VALUES (?, ?, ?, ?)",
            (session_id, f"uploads/demo_shot_{session_id}.png", 1280, 720),
        )
        screenshot_id = shot_cur.lastrowid

        # Bug reports
        for _ in range(bugs_found):
            btype = random.choice(BUG_TYPES)
            bbox = json.dumps({
                "x": random.randint(0, 1100),
                "y": random.randint(0, 600),
                "w": random.randint(50, 200),
                "h": random.randint(20, 100),
            })
            db.execute(
                """INSERT INTO bug_reports
                   (session_id, screenshot_id, bug_type, severity, confidence,
                    bounding_box, description)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    session_id,
                    screenshot_id,
                    btype,
                    random.choice(SEVERITIES),
                    round(random.uniform(0.52, 0.99), 4),
                    bbox,
                    DESCRIPTIONS[btype],
                ),
            )

    # ── Model Metrics ─────────────────────────────────────────────────────────
    for epoch in range(1, 21):
        train_acc = min(0.60 + epoch * 0.018 + random.uniform(-0.005, 0.005), 0.99)
        val_acc   = min(0.58 + epoch * 0.016 + random.uniform(-0.008, 0.008), 0.97)
        train_loss = max(1.2 - epoch * 0.055 + random.uniform(-0.01, 0.01), 0.05)
        val_loss   = max(1.3 - epoch * 0.058 + random.uniform(-0.01, 0.01), 0.06)
        db.execute(
            """INSERT INTO model_metrics
               (epoch, train_acc, val_acc, train_loss, val_loss, precision, recall, f1_score)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (epoch, round(train_acc, 4), round(val_acc, 4),
             round(train_loss, 4), round(val_loss, 4),
             round(random.uniform(0.80, 0.96), 4),
             round(random.uniform(0.78, 0.94), 4),
             round(random.uniform(0.79, 0.95), 4)),
        )

    # ── Contact stubs ─────────────────────────────────────────────────────────
    db.execute(
        """INSERT INTO contacts (name, email, subject, message) VALUES
           ('Alice Wong', 'alice@ml.dev', 'Feature Request',
            'Could you add support for mobile viewport testing?')""",
    )
    db.commit()
    print("✓ Seed data loaded: 3 users, 15 sessions, bug reports, 20 metric epochs.")
