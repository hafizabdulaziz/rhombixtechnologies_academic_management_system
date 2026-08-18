from database import get_connection
from security import hash_password, validate_password
from activity_logs import log_activity
import session
import sqlite3
from datetime import datetime

# Stubs removed; functionality now fully imported/implemented
# and circular dependencies resolved via local imports in login().

def email_exists(email):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT id FROM users WHERE email = ?",
        (email,) 
    )

    user = cursor.fetchone()
    connection.close()
    return user

def signup():
    print("\n==== SIGN UP ====")
    email = input("Enter Email: ").strip()
    if email_exists(email):
        print("Email already exists.")
        return
    while True:
        password = input("Enter Password: ")
        if validate_password(password):
            break
    hashed_password = hash_password(password)
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO users
        (
            email,
            password,
            created_at,
            role
        )
        VALUES
        (?,?,?,?)
        """,
        (
            email,
            hashed_password,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "student"
        )
    )

    connection.commit()
    connection.close()
    print("Signup Successful.")
    session.current_user = verify_login(email, password)[0]
    print("Login Successfully.")
    log_activity("SIGNUP", "New student account created.")
    
    from student import create_student_profile as create_profile
    from marks import add_subjects as add_subs
    from student import student_dashboard as dashboard
    
    create_profile()
    add_subs()
    dashboard()
    return

def verify_login(email, password):
    connection = get_connection()
    cursor = connection.cursor()
    hashed_password = hash_password(password)

    cursor.execute(
        """
        SELECT id, role
        FROM users
        WHERE email = ?
        AND password = ?
        """,
        (
        email,
        hashed_password
        )
    )

    user = cursor.fetchone()
    connection.close()
    return user

def get_current_user_role():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT role
        FROM users
        WHERE id = ?
        """,
        (session.current_user,)
    )

    user = cursor.fetchone()
    connection.close()

    if not user:
        return None

    return user[0]

def require_role(*allowed_roles):
    if session.current_user is None:
        print("Access Denied. Please login first.")
        return False

    role = get_current_user_role()

    if role not in allowed_roles:
        print("Access Denied. You do not have permission.")
        return False

    return True

def login():
    print("\n==== LOGIN ====")

    email = input("Enter Email: ").strip()
    password = input("Enter Password: ")

    user = verify_login(email, password)

    if not user:
        print("Invalid Email or Password.")
        return

    session.current_user = user[0]
    role = user[1]

    print("Login Successful.")
    log_activity("LOGIN", "User logged into the system.")

    if role == "admin":
        from admin import admin_dashboard
        admin_dashboard()

    elif role == "teacher":
        from teacher import teacher_dashboard
        teacher_dashboard()

    elif role == "student":
        # Local imports to avoid circular dependencies
        from student import student_profile_exists
        from student import create_student_profile as create_profile
        from student import student_dashboard as dashboard
        from marks import subjects_already_exist
        from marks import add_subjects as add_subs
        
        if not student_profile_exists(session.current_user):
            create_profile()

        if not subjects_already_exist():
            add_subs()

        dashboard()

    else:
        print("Unknown User Role.")

def get_current_user_email():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT email
        FROM users
        WHERE id = ?
        """,
        (session.current_user,)
    )
    user = cursor.fetchone()
    connection.close()
    if not user:
        return None
    return user[0]

def change_password():
    print("\n===== CHANGE PASSWORD =====")
    current_password = input("Enter Current Password: ")
    user = verify_login(
        get_current_user_email(),
        current_password
    )
    if not user:
        print("Current Password is incorrect.")
        return

    while True:
        new_password = input("Enter New Password: ")

        if validate_password(new_password):
            break

    if new_password == current_password:
        print("New password cannot be the same as current password.")
        return

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE users
        SET password = ?
        WHERE id = ?
        """,
        (
            hash_password(new_password),
            session.current_user
        )
    )

    connection.commit()
    connection.close()
    log_activity("PASSWORD_CHANGE", "User changed password.")
    print("Password Changed Successfully.")

# Refined local imports to prevent circular dependencies at runtime.
