import sys
import getpass

from database.database import init_db
from database.employee_repo import add_admin, verify_admin


def create_admin(username, password):
    existing = verify_admin(username, "")  # cheap existence probe won't match password, but we check properly below
    from database.database import get_connection
    conn = get_connection()
    row = conn.execute("SELECT id FROM admins WHERE username = ?", (username,)).fetchone()
    conn.close()

    if row:
        print(f"ERROR: An admin with username '{username}' already exists.")
        return False

    if len(password) < 6:
        print("ERROR: Password must be at least 6 characters.")
        return False

    admin_id = add_admin(username, password)
    print(f"SUCCESS: Admin '{username}' created (id: {admin_id}).")
    return True


if __name__ == "__main__":
    init_db()

    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        username = input("Admin username: ").strip()

    password = getpass.getpass("Admin password (input hidden): ")
    confirm = getpass.getpass("Confirm password: ")

    if password != confirm:
        print("ERROR: Passwords do not match.")
        sys.exit(1)

    create_admin(username, password)
