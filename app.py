import base64
import numpy as np
import cv2
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from datetime import datetime

from database.database import init_db, get_connection
from database.employee_repo import (
    verify_pin, mark_attendance, get_employee_by_code, verify_admin,
    get_all_employee_embeddings
)
from ai.face_recognizer import get_embedding_from_image, cosine_similarity, RECOGNITION_THRESHOLD

from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

init_db()


def login_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not session.get('admin_username'):
            return redirect(url_for('login'))
        return view_func(*args, **kwargs)
    return wrapped


@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        admin = verify_admin(username, password)
        if admin:
            session['admin_username'] = admin['username']
            return redirect(url_for('dashboard'))
        else:
            error = "Invalid username or password."

    return render_template('login.html', error=error)


@app.route('/admin/logout')
def logout():
    session.pop('admin_username', None)
    return redirect(url_for('login'))


@app.route('/')
@login_required
def dashboard():
    conn = get_connection()
    today = datetime.now().strftime('%Y-%m-%d')

    total_employees = conn.execute(
        "SELECT COUNT(*) as c FROM employees WHERE status = 'active'"
    ).fetchone()['c']

    present_today = conn.execute(
        "SELECT COUNT(*) as c FROM attendance WHERE date = ?", (today,)
    ).fetchone()['c']

    # Full today's attendance: every active employee, with their check-in if they have one
    all_today = conn.execute("""
        SELECT e.employee_code, e.name, a.check_in_time, a.method
        FROM employees e
        LEFT JOIN attendance a ON e.id = a.employee_id AND a.date = ?
        WHERE e.status = 'active'
        ORDER BY (a.check_in_time IS NULL) ASC, a.check_in_time DESC
    """, (today,)).fetchall()
    conn.close()

    return render_template(
        'dashboard.html',
        total_employees=total_employees,
        present_today=present_today,
        absent_today=max(total_employees - present_today, 0),
        recent=all_today,
        today=today
    )


@app.route('/employees')
@login_required
def employees():
    conn = get_connection()
    today = datetime.now().strftime('%Y-%m-%d')

    rows = conn.execute("""
        SELECT e.employee_code, e.name, e.department, e.position,
               e.verification_method, e.status,
               a.check_in_time, a.method as attendance_method
        FROM employees e
        LEFT JOIN attendance a ON e.id = a.employee_id AND a.date = ?
        ORDER BY e.id
    """, (today,)).fetchall()
    conn.close()
    return render_template('employees.html', employees=rows)


@app.route('/attendance/pin', methods=['GET', 'POST'])
@login_required
def attendance_pin():
    result_message = None
    result_success = None

    if request.method == 'POST':
        employee_code = request.form.get('employee_code', '').strip()
        pin = request.form.get('pin', '').strip()

        employee = verify_pin(employee_code, pin)

        if not employee:
            result_message = "Verification failed. Check your Employee ID and PIN."
            result_success = False
        else:
            marked = mark_attendance(employee['id'], method='pin')
            if marked:
                result_message = f"Attendance marked for {employee['name']} ({employee_code})."
                result_success = True
            else:
                result_message = f"{employee['name']} has already checked in today."
                result_success = False

    return render_template('pin_attendance.html', message=result_message, success=result_success)


@app.route('/attendance')
def attendance_portal():
    return render_template('attendance_portal.html')


@app.route('/attendance/pin-kiosk', methods=['GET', 'POST'])
def attendance_pin_kiosk():
    result_message = None
    result_success = None

    if request.method == 'POST':
        employee_code = request.form.get('employee_code', '').strip()
        pin = request.form.get('pin', '').strip()

        employee = verify_pin(employee_code, pin)

        if not employee:
            result_message = "Verification failed. Check your Employee ID and PIN."
            result_success = False
        else:
            marked = mark_attendance(employee['id'], method='pin')
            if marked:
                result_message = f"Attendance marked for {employee['name']} ({employee_code})."
                result_success = True
            else:
                result_message = f"{employee['name']} has already checked in today."
                result_success = False

    return render_template('kiosk_pin_attendance.html', message=result_message, success=result_success)


@app.route('/attendance/face')
def attendance_face():
    return render_template('face_attendance.html')


@app.route('/attendance/face/verify', methods=['POST'])
def attendance_face_verify():
    data = request.get_json(silent=True)
    if not data or 'image' not in data:
        return jsonify({'status': 'error', 'message': 'No image received.'}), 400

    try:
        header, encoded = data['image'].split(',', 1)
        img_bytes = base64.b64decode(encoded)
        img_array = np.frombuffer(img_bytes, dtype=np.uint8)
        frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    except Exception:
        return jsonify({'status': 'error', 'message': 'Could not decode image.'}), 400

    if frame is None:
        return jsonify({'status': 'error', 'message': 'Could not decode image.'}), 400

    embedding, face_count = get_embedding_from_image(frame)

    if face_count == 0:
        return jsonify({'status': 'no_face'})

    known = get_all_employee_embeddings()
    best_match = None
    best_score = -1
    for employee_id, code, name, known_embedding in known:
        score = cosine_similarity(embedding, known_embedding)
        if score > best_score:
            best_score = score
            best_match = (employee_id, code, name)

    if not best_match or best_score < RECOGNITION_THRESHOLD:
        return jsonify({'status': 'unknown'})

    employee_id, code, name = best_match
    marked = mark_attendance(employee_id, method='face')

    if marked:
        return jsonify({'status': 'match', 'name': name, 'code': code, 'score': round(best_score, 2)})
    else:
        return jsonify({'status': 'duplicate', 'name': name, 'code': code})


if __name__ == '__main__':
    app.run(debug=False)