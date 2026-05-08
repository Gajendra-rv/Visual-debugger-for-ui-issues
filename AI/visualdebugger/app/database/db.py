"""SQLite connection manager using Flask's application context."""
import sqlite3
import os
import click
from flask import g, current_app


def get_db():
    """Return the database connection for the current request context."""
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
        g.db.execute("PRAGMA journal_mode = WAL")
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Initialize the database from schema.sql."""
    db = get_db()
    schema_path = current_app.config["SCHEMA"]
    with open(schema_path, "r") as f:
        db.executescript(f.read())
    db.commit()
    current_app.logger.info("Database initialized from schema.sql")


def init_app(app):
    app.teardown_appcontext(close_db)

    @app.cli.command("init-db")
    def init_db_command():
        """Clear existing data and create fresh tables."""
        init_db()
        click.echo("✓ Database initialized.")

    @app.cli.command("seed-db")
    def seed_db_command():
        """Seed the database with demo data."""
        from app.database.seed import seed_all
        seed_all()
        click.echo("✓ Database seeded with demo data.")

    # Auto-initialize DB if it doesn't exist
    with app.app_context():
        if not os.path.exists(app.config["DATABASE"]):
            init_db()
