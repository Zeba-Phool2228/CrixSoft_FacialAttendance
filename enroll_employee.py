import sys
import cv2

from database.database import init_db
from database.employee_repo import add_employee, save_embedding, get_employee_by_code
from ai.face_recognizer import get_embedding_from_image


def enroll_with_face(employee_code, name, image_path, department=None, position=None, email=None):
    existing = get_employee_by_code(employee_code)
    if existing:
        print(
            f"ERROR: Employee code '{employee_code}' already exists (name: {existing['name']}).")
        return False

    img = cv2.imread(image_path)
    if img is None:
        print(
            f"ERROR: Could not read image at '{image_path}'. Check the path.")
        return False

    embedding, face_count = get_embedding_from_image(img)

    if face_count == 0:
        print("ERROR: No face detected in the image. Use a clear, front-facing photo.")
        return False
    if face_count > 1:
        print(
            f"ERROR: {face_count} faces detected. Enrollment image must contain exactly ONE face.")
        return False

    employee_id = add_employee(employee_code, name, department, position, email,
                               verification_method='face')
    save_embedding(employee_id, embedding)

    print(
        f"SUCCESS: Enrolled '{name}' (code: {employee_code}, id: {employee_id}) using FACE verification.")
    return True


def enroll_with_pin(employee_code, name, pin, department=None, position=None, email=None):
    existing = get_employee_by_code(employee_code)
    if existing:
        print(
            f"ERROR: Employee code '{employee_code}' already exists (name: {existing['name']}).")
        return False

    if not pin or len(pin) < 4:
        print("ERROR: PIN must be at least 4 digits/characters.")
        return False

    employee_id = add_employee(employee_code, name, department, position, email,
                               verification_method='pin', pin=pin)

    print(
        f"SUCCESS: Enrolled '{name}' (code: {employee_code}, id: {employee_id}) using PIN verification.")
    return True


def print_usage():
    print("Usage:")
    print(
        "  Face-based:  python enroll_employee.py face <employee_code> <name> <image_path> [department] [position]")
    print(
        "  PIN-based:   python enroll_employee.py pin <employee_code> <name> <pin> [department] [position]")


if __name__ == "__main__":
    init_db()

    if len(sys.argv) < 5:
        print_usage()
        sys.exit(1)

    mode = sys.argv[1].lower()
    code = sys.argv[2]
    emp_name = sys.argv[3]
    dept = sys.argv[5] if len(sys.argv) > 5 else None
    pos = sys.argv[6] if len(sys.argv) > 6 else None

    if mode == "face":
        image = sys.argv[4]
        enroll_with_face(code, emp_name, image, department=dept, position=pos)
    elif mode == "pin":
        pin_value = sys.argv[4]
        enroll_with_pin(code, emp_name, pin_value,
                        department=dept, position=pos)
    else:
        print(f"ERROR: Unknown mode '{mode}'. Use 'face' or 'pin'.")
        print_usage()
