"""User model — thin wrapper around SQLite rows."""
from werkzeug.security import generate_password_hash, check_password_hash
from app.database.db import get_db


class User:
    def __init__(self, row):
        self.id           = row["id"]
        self.username     = row["username"]
        self.email        = row["email"]
        self.password_hash = row["password_hash"]
        self.role         = row["role"]
        self.avatar_url   = row["avatar_url"]
        self.bio          = row["bio"]
        self.is_active    = bool(row["is_active"])
        self.created_at   = row["created_at"]

    # ── Flask-Login interface ─────────────────────────────────────────────────
    @property
    def is_authenticated(self): return True
    @property
    def is_anonymous(self): return False
    def get_id(self): return str(self.id)

    # ── Helpers ───────────────────────────────────────────────────────────────
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # ── DB queries ────────────────────────────────────────────────────────────
    @staticmethod
    def get_by_id(user_id):
        row = get_db().execute(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        return User(row) if row else None

    @staticmethod
    def get_by_email(email):
        row = get_db().execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()
        return User(row) if row else None

    @staticmethod
    def get_by_username(username):
        row = get_db().execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        return User(row) if row else None

    @staticmethod
    def create(username, email, password, role="user"):
        db = get_db()
        db.execute(
            "INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
            (username, email, generate_password_hash(password), role),
        )
        db.commit()
        return User.get_by_email(email)

    def update_profile(self, username=None, bio=None, avatar_url=None):
        db = get_db()
        if username:
            db.execute("UPDATE users SET username=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
                       (username, self.id))
        if bio is not None:
            db.execute("UPDATE users SET bio=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
                       (bio, self.id))
        if avatar_url is not None:
            db.execute("UPDATE users SET avatar_url=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
                       (avatar_url, self.id))
        db.commit()

    def change_password(self, new_password):
        db = get_db()
        db.execute(
            "UPDATE users SET password_hash=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
            (generate_password_hash(new_password), self.id),
        )
        db.commit()
