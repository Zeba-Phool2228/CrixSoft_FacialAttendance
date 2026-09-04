import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))), 'attendance.db')


def get_connection():
    """Returns a new SQLite connection with foreign keys enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Creates all required tables if they do not already exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            department TEXT,
            position TEXT,
            email TEXT,
            status TEXT DEFAULT 'active',
            verification_method TEXT DEFAULT 'face',
            pin_hash TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS embeddings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            embedding BLOB NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            check_in_time TEXT NOT NULL,
            method TEXT DEFAULT 'live',
            status TEXT DEFAULT 'present',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
            UNIQUE(employee_id, date)
        )
    """)

    # --- Migration: add new columns if this DB already existed before this change ---
    cursor.execute("PRAGMA table_info(employees)")
    existing_columns = [row[1] for row in cursor.fetchall()]

    if "verification_method" not in existing_columns:
        cursor.execute(
            "ALTER TABLE employees ADD COLUMN verification_method TEXT DEFAULT 'face'")
        print("Migrated: added verification_method column.")

    if "pin_hash" not in existing_columns:
        cursor.execute("ALTER TABLE employees ADD COLUMN pin_hash TEXT")
        print("Migrated: added pin_hash column.")

    conn.commit()
    conn.close()
    print("Database initialized successfully at:", DB_PATH)


if __name__ == "__main__":
    init_db()
