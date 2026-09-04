import numpy as np
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from database.database import get_connection


def add_employee(employee_code, name, department=None, position=None, email=None,
                 verification_method='face', pin=None):
    pin_hash = generate_password_hash(pin) if (
        verification_method == 'pin' and pin) else None

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO employees (employee_code, name, department, position, email, verification_method, pin_hash)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (employee_code, name, department, position,
         email, verification_method, pin_hash)
    )
    employee_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return employee_id


def save_embedding(employee_id, embedding):
    conn = get_connection()
    cursor = conn.cursor()
    embedding_bytes = embedding.astype(np.float32).tobytes()
    cursor.execute(
        "INSERT INTO embeddings (employee_id, embedding) VALUES (?, ?)",
        (employee_id, embedding_bytes)
    )
    conn.commit()
    conn.close()


def get_all_employee_embeddings():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT e.id, e.employee_code, e.name, emb.embedding
        FROM embeddings emb
        JOIN employees e ON e.id = emb.employee_id
        WHERE e.status = 'active'
    """)
    rows = cursor.fetchall()
    conn.close()

    results = []
    for row in rows:
        embedding = np.frombuffer(row["embedding"], dtype=np.float32)
        results.append(
            (row["id"], row["employee_code"], row["name"], embedding))
    return results


def get_employee_by_code(employee_code):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM employees WHERE employee_code = ?", (employee_code,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def verify_pin(employee_code, pin):
    employee = get_employee_by_code(employee_code)
    if not employee:
        return None
    if employee['verification_method'] != 'pin':
        return None
    if not employee['pin_hash']:
        return None
    if check_password_hash(employee['pin_hash'], pin):
        return employee
    return None


def has_attended_today(employee_id):
    """Returns True if this employee already has an attendance record for today's date."""
    today = datetime.now().strftime('%Y-%m-%d')
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id FROM attendance WHERE employee_id = ? AND date = ?",
        (employee_id, today)
    )
    row = cursor.fetchone()
    conn.close()
    return row is not None


def mark_attendance(employee_id, method='live'):
    """
    Inserts a new attendance record for today, if one doesn't already exist.
    method: 'face' or 'pin' (or 'live' as a generic default).
    Returns True if a new record was inserted, False if already marked today.
    """
    if has_attended_today(employee_id):
        return False

    today = datetime.now().strftime('%Y-%m-%d')
    now_time = datetime.now().strftime('%H:%M:%S')

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """INSERT INTO attendance (employee_id, date, check_in_time, method, status)
               VALUES (?, ?, ?, ?, 'present')""",
            (employee_id, today, now_time, method)
        )
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        return False
    finally:
        conn.close()


def add_admin(username, password):
    """
    Creates a new admin account. Returns the new admin's id.
    Raises sqlite3.IntegrityError if the username already exists.
    Intended to be called only from a trusted bootstrap script, not a public route.
    """
    password_hash = generate_password_hash(password)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO admins (username, password_hash) VALUES (?, ?)",
        (username, password_hash)
    )
    admin_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return admin_id


def verify_admin(username, password):
    """
    Verifies admin login credentials.
    Returns the admin dict (id, username, created_at) if valid, otherwise None.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM admins WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None
    admin = dict(row)
    if check_password_hash(admin['password_hash'], password):
        return admin
    return None
