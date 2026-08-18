import sqlite3
import hashlib
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import csv

DATABASE = "student_tracker.db"
MIN_PASSWORD_LENGHT = 8
PASS_MARKS_PERCENTAGE = 40

def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def validate_password(password):
    if len(password) < MIN_PASSWORD_LENGHT:
        print(
            f"Password must be atleast "
            f"{MIN_PASSWORD_LENGHT} characters long."
        )
        return False
    if password.isalpha():
        print("Password must contain at least one number.")
        return False
    if password.isdigit():
        print("Password must contain at least one letter.")
        return False
    return True

def initialize_database():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'student'
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            roll_number TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            date_of_birth TEXT,
            school TEXT NOT NULL,
            class_name TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    cursor.execute("""
    INSERT OR IGNORE INTO users
    (
    email,
    password,
    created_at,
    role
    )
    VALUES
    (
    ?,
    ?,
    ?,
    ?
    )
    """,
    (
    "abdulaziz555@gmail.com",
    hash_password("admin123"),
    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "admin"
    ))

    cursor.execute("""
        INSERT OR IGNORE INTO users
        (
            email,
            password,
            created_at,
            role
        )
        VALUES
        (
            ?,
            ?,
            ?,
            ?
        )
    """,
    (
        "teacher@school.com",
        hash_password("teacher123"),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "teacher"
    ))

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            subject_name TEXT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students(id),
            UNIQUE(student_id, subject_name)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS marks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            subject_id INTEGER NOT NULL,
            obtained_marks REAL NOT NULL,
            total_marks REAL NOT NULL,
            FOREIGN KEY(student_id) REFERENCES students(id),
            FOREIGN KEY(subject_id) REFERENCES subjects(id),
            UNIQUE(student_id, subject_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            attendance_date TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY(student_id) REFERENCES students(id),
            UNIQUE(student_id, attendance_date)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activity_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT NOT NULL,
            details TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    connection.commit()
    connection.close()
initialize_database()
current_user = None
print("Database initialized successfully.")

def log_activity(action, details=""):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO activity_logs
        (
            user_id,
            action,
            details,
            created_at
        )
        VALUES
        (?,?,?,?)
        """,
        (
            current_user,
            action,
            details,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    )

    connection.commit()
    connection.close()

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
    global current_user
    current_user = verify_login(email, password)[0]
    print("Login Successfully.")
    log_activity("SIGNUP", "New student account created.")
    create_student_profile()
    add_subjects()
    student_dashboard()
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
        (current_user,)
    )

    user = cursor.fetchone()
    connection.close()

    if not user:
        return None

    return user[0]

def require_role(*allowed_roles):
    if current_user is None:
        print("Access Denied. Please login first.")
        return False

    role = get_current_user_role()

    if role not in allowed_roles:
        print("Access Denied. You do not have permission.")
        return False

    return True

def login():
    global current_user

    print("\n==== LOGIN ====")

    email = input("Enter Email: ").strip()
    password = input("Enter Password: ")

    user = verify_login(email, password)

    if not user:
        print("Invalid Email or Password.")
        return

    current_user = user[0]
    role = user[1]

    print("Login Successful.")
    log_activity("LOGIN", "User logged into the system.")

    if role == "admin":
        admin_dashboard()

    elif role == "teacher":
        teacher_dashboard()

    elif role == "student":

        if not student_profile_exists(current_user):
            create_student_profile()

        if not subjects_already_exist():
            add_subjects()

        student_dashboard()

    else:
        print("Unknown User Role.")
        
def student_profile_exists(user_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id
        FROM students
        WHERE user_id = ?
        """,
        (user_id,)
    )

    student = cursor.fetchone()
    connection.close()
    return student is not None

def create_student_profile():
    while True:
        roll_number = input("Enter Roll Number: ").strip()

        if not roll_number:
            print("Roll Number cannot be empty.")
            continue

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id
            FROM students
            WHERE roll_number = ?
            """,
            (roll_number,)
        )

        existing_student = cursor.fetchone()
        connection.close()

        if existing_student:
            print("Roll Number already exists.")
            continue

        break

    while True:
        name = input("Enter Name: ").strip()

        if not name:
            print("Name cannot be empty.")

        elif not name.replace(" ", "").isalpha():
            print("Name can contain letters and spaces only.")

        else:
            break

    while True:
        email = input("Enter Email Address: ").strip()

        if not email:
            print("Email cannot be empty.")
            continue

        if "@" not in email or "." not in email:
            print("Please enter a valid email.")
            continue

        break

    while True:
        school = input("Enter School Name: ").strip()

        if not school:
            print("School name cannot be empty.")

        else:
            break

    while True:
        class_name = input("Enter Class: ").strip()

        if not class_name:
            print("Class cannot be empty.")

        else:
            break

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO students
        (
            user_id,
            roll_number,
            name,
            email,
            school,
            class_name
        )
        VALUES
        (?,?,?,?,?,?)
        """,
        (
            current_user,
            roll_number,
            name,
            email,
            school,
            class_name
        )
    )

    connection.commit()
    connection.close()

    print("Student Profile Created Successfully.")

def get_student_id():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id
        FROM students
        WHERE user_id = ?
        """,
        (current_user,)
    ) 

    student = cursor.fetchone()
    connection.close()
    if not student:
        return None
    return student[0]

def subjects_already_exist():
    student_id = get_student_id()
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id
        FROM subjects
        WHERE student_id = ?
        """,
        (student_id,)
    )

    subject = cursor.fetchone()
    connection.close()

    return subject is not None

def add_subjects():
    student_id = get_student_id()

    if not student_id:
        print("Student Profile Not Found.")
        return

    while True:
        try:
            how_many = int(input("How many New Subjects?: "))

            if how_many <= 0:
                print("Please enter a number greater than 0.")
                continue

            break

        except ValueError:
            print("Please enter numbers only.")

    connection = get_connection()
    cursor = connection.cursor()

    added_count = 0

    for i in range(how_many):

        while True:
            subject_name = input(
                f"Enter New Subject {i + 1}: "
            ).strip()

            if not subject_name:
                print("Subject name cannot be empty.")
                continue

            break

        try:
            cursor.execute(
                """
                INSERT INTO subjects
                (
                    student_id,
                    subject_name
                )
                VALUES
                (?,?)
                """,
                (
                    student_id,
                    subject_name
                )
            )

            print(f"{subject_name} Added Successfully.")
            added_count += 1

        except sqlite3.IntegrityError:
            print(f"{subject_name} Already Exists.")

    connection.commit()
    connection.close()

    print(f"\n{added_count} New Subject(s) Added Successfully.")

def view_profile():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            roll_number,
            name,
            email,
            school,
            class_name
        FROM students
        WHERE user_id = ?
        """,
        (current_user,)
    )

    student = cursor.fetchone()

    if not student:
        print("Student Profile Not Found.")
        connection.close()
        return

    cursor.execute(
        """
        SELECT subject_name
        FROM subjects
        WHERE student_id = (
            SELECT id
            FROM students
            WHERE user_id = ?
        )
        ORDER BY subject_name
        """,
        (current_user,)
    )

    subjects = cursor.fetchall()

    print("\n========================")
    print("STUDENT PROFILE")
    print("========================")
    print(f"Roll Number : {student[0]}")
    print(f"Name        : {student[1]}")
    print(f"Email       : {student[2]}")
    print(f"School      : {student[3]}")
    print(f"Class       : {student[4]}")

    print("\nSubjects:")

    if subjects:
        for subject in subjects:
            print(f"- {subject[0]}")
    else:
        print("No Subject Added.")

    connection.close()

def get_current_user_email():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT email
        FROM users
        WHERE id = ?
        """,
        (current_user,)
    )
    user = cursor.fetchone()
    connection.close()
    if not user:
        return None
    return user[0]
    
def change_password():
    global current_user
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
            current_user
        )
    )

    connection.commit()
    connection.close()
    log_activity("PASSWORD_CHANGE", "User changed password.")
    print("Password Changed Successfully.")

def update_profile():
    while True:
        print("\n===== UPDATE PROFILE =====")
        print("1. Change Name")
        print("2. Change School")
        print("3. Change Class")
        print("4. Back")

        choice = input("Enter Choice: ").strip()

        if choice == "4":

            break

        if choice not in ["1", "2", "3"]:
            print("Invalid Choice.")
            continue

        if choice == "1":
            while True:
                name = input("Enter New Name: ").strip()

                if not name:
                    print("Name cannot be empty.")
                    continue

                break

            connection = get_connection()
            cursor = connection.cursor()

            cursor.execute(
                """
                UPDATE students
                SET name = ?
                WHERE user_id = ?
                """,
                (name, current_user)
            )

            connection.commit()
            connection.close()

            print("Name Updated Successfully.")

        elif choice == "2":
            while True:
                school = input("Enter New School: ").strip()

                if not school:
                    print("School name cannot be empty.")
                    continue

                break

            connection = get_connection()
            cursor = connection.cursor()

            cursor.execute(
                """
                UPDATE students
                SET school = ?
                WHERE user_id = ?
                """,
                (school, current_user)
            )

            connection.commit()
            connection.close()

            print("School Updated Successfully.")

        elif choice == "3":
            while True:
                class_name = input("Enter New Class: ").strip()

                if not class_name:
                    print("Class cannot be empty.")
                    continue

                break

            connection = get_connection()
            cursor = connection.cursor()

            cursor.execute(
                """
                UPDATE students
                SET class_name = ?
                WHERE user_id = ?
                """,
                (class_name, current_user)
            )

            connection.commit()
            connection.close()

            print("Class Updated Successfully.")

def add_marks():
    if not require_role("teacher", "admin"):
        return 
    print("\n========================")
    print("SELECT STUDENT")
    print("========================")

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            roll_number,
            name,
            email,
            class_name
        FROM students
        ORDER BY roll_number
        """
    )

    students = cursor.fetchall()
    connection.close()

    if not students:
        print("No Students Found.")
        return

    for i, student in enumerate(students, start=1):
        print(
            f"{i}. Roll No: {student[1]} | "
            f"Name: {student[2]} | "
            f"Class: {student[4]}"
        )

    print(f"{len(students) + 1}. Back")

    while True:
        try:
            student_choice = int(
                input("\nSelect Student: ")
            )
        except ValueError:
            print("Please enter a number.")
            continue

        if student_choice == len(students) + 1:
            return

        if student_choice < 1 or student_choice > len(students):
            print("Invalid Choice.")
            continue

        break

    selected_student = students[student_choice - 1]
    student_id = selected_student[0]

    print("\n========================")
    print("SELECTED STUDENT")
    print("========================")
    print(f"Roll Number : {selected_student[1]}")
    print(f"Name        : {selected_student[2]}")
    print(f"Email       : {selected_student[3]}")
    print(f"Class       : {selected_student[4]}")
    while True:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                subjects.id,
                subjects.subject_name,
                marks.obtained_marks,
                marks.total_marks
            FROM subjects
            LEFT JOIN marks
            ON subjects.id = marks.subject_id
            AND marks.student_id = ?
            WHERE subjects.student_id = ?
            ORDER BY subjects.subject_name
            """,
            (student_id, student_id)
        )

        subjects = cursor.fetchall()
        connection.close()

        if not subjects:
            print("\nNo Subjects Found For This Student.")
            return

        print("\n========================")
        print("ADD / UPDATE MARKS")
        print("========================")

        for i, subject in enumerate(subjects, start=1):

            if subject[2] is None:
                marks_status = "Not Added"
            else:
                marks_status = (
                    f"{subject[2]:g}/{subject[3]:g}"
                )

            print(
                f"{i}. {subject[1]} - {marks_status}"
            )

        print(f"{len(subjects) + 1}. Back")

        try:
            choice = int(
                input("\nSelect Subject: ")
            )
        except ValueError:
            print("Please enter a number.")
            continue

        if choice == len(subjects) + 1:
            break

        if choice < 1 or choice > len(subjects):
            print("Invalid Choice.")
            continue

        selected_subject = subjects[choice - 1]

        print(
            f"\n===== {selected_subject[1]} ====="
        )

        while True:
            try:
                obtained = float(
                    input("Obtained Marks: ")
                )

                total = float(
                    input("Total Marks: ")
                )

                if obtained < 0:
                    print(
                        "Obtained Marks cannot be negative."
                    )
                    continue

                if total <= 0:
                    print(
                        "Total Marks must be greater than 0."
                    )
                    continue

                if obtained > total:
                    print(
                        "Obtained Marks cannot be greater "
                        "than Total Marks."
                    )
                    continue

                break

            except ValueError:
                print("Please enter numbers only.")

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO marks
            (
                student_id,
                subject_id,
                obtained_marks,
                total_marks
            )
            VALUES
            (?,?,?,?)
            """,
            (
                student_id,
                selected_subject[0],
                obtained,
                total
            )
        )

        connection.commit()
        connection.close()

        print(
            f"{selected_subject[1]} Marks "
            f"Saved Successfully."
        )
        log_activity(
            "MARKS_UPDATED",
            f"Marks updated for {selected_subject[1]}."
        )

def view_result():
    student_id = get_student_id()

    if not student_id:
        print("Student Profile Not Found.")
        return

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            subjects.subject_name,
            marks.obtained_marks,
            marks.total_marks
        FROM subjects
        JOIN marks
        ON subjects.id = marks.subject_id
        WHERE subjects.student_id = ?
        ORDER BY subjects.subject_name
        """,
        (student_id,)
    )

    result = cursor.fetchall()
    connection.close()

    if not result:
        print("No Result Found.")
        return

    total_obtained = 0
    total_marks = 0
    failed_subjects = []
    subject_analytics = []

    for subject in result:
        subject_name = subject[0]
        obtained = subject[1]
        total = subject[2]

        percentage = (obtained / total) * 100

        total_obtained += obtained
        total_marks += total

        subject_analytics.append(
            (
                subject_name,
                obtained,
                total,
                percentage
            )
        )

        if percentage < PASS_MARKS_PERCENTAGE:
            failed_subjects.append(subject_name)

    overall_percentage = (
        total_obtained / total_marks
    ) * 100

    if overall_percentage >= 90:
        grade = "A+"
    elif overall_percentage >= 80:
        grade = "A"
    elif overall_percentage >= 70:
        grade = "B"
    elif overall_percentage >= 60:
        grade = "C"
    elif overall_percentage >= 50:
        grade = "D"
    elif overall_percentage >= PASS_MARKS_PERCENTAGE:
        grade = "E"
    else:
        grade = "F"

    highest_subject = max(
        subject_analytics,
        key=lambda subject: subject[3]
    )

    lowest_subject = min(
        subject_analytics,
        key=lambda subject: subject[3]
    )

    if failed_subjects:
        status = "REAPPEAR"
    elif overall_percentage >= PASS_MARKS_PERCENTAGE:
        status = "PASS"
    else:
        status = "FAIL"

    print("\n========================================")
    print("STUDENT RESULT")
    print("========================================")

    print("\nSUBJECT-WISE ANALYTICS")
    print("----------------------------------------")

    for subject in subject_analytics:
        print(
            f"{subject[0]:20} "
            f"{subject[1]:.0f}/{subject[2]:.0f} "
            f"({subject[3]:.2f}%)"
        )

    print("\n========================================")
    print("OVERALL ANALYTICS")
    print("========================================")

    print(f"Total Marks       : {total_marks:.0f}")
    print(f"Obtained Marks    : {total_obtained:.0f}")
    print(f"Overall Percentage: {overall_percentage:.2f}%")
    print(f"Grade             : {grade}")
    print(f"Status            : {status}")

    print("\n----------------------------------------")
    print("SUBJECT PERFORMANCE")
    print("----------------------------------------")

    print(
        f"Highest Subject   : {highest_subject[0]} "
        f"({highest_subject[3]:.2f}%)"
    )

    print(
        f"Lowest Subject    : {lowest_subject[0]} "
        f"({lowest_subject[3]:.2f}%)"
    )

    if failed_subjects:
        print("\n----------------------------------------")
        print("FAILED SUBJECTS")
        print("----------------------------------------")

        for subject in failed_subjects:
            print(f"- {subject}")

    print("========================================")

def export_result_csv():
    student_id = get_student_id()

    if not student_id:
        print("Student Profile Not Found.")
        return

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            students.roll_number,
            students.name,
            students.email,
            subjects.subject_name,
            marks.obtained_marks,
            marks.total_marks
        FROM students
        JOIN subjects
        ON students.id = subjects.student_id
        LEFT JOIN marks
        ON subjects.id = marks.subject_id
        AND marks.student_id = students.id
        WHERE students.id = ?
        ORDER BY subjects.subject_name
        """,
        (student_id,)
    )

    result = cursor.fetchall()
    connection.close()

    if not result:
        print("No Result Found.")
        return

    filename = f"student_result_{result[0][0]}.csv"

    with open(
        filename,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "Roll Number",
            "Name",
            "Email",
            "Subject",
            "Obtained Marks",
            "Total Marks",
            "Percentage"
        ])

        for row in result:

            obtained = row[4]
            total = row[5]

            if obtained is None or total is None:
                percentage = "Marks Not Added"
            else:
                percentage = f"{(obtained / total) * 100:.2f}%"

            writer.writerow([
                row[0],
                row[1],
                row[2],
                row[3],
                obtained if obtained is not None else "",
                total if total is not None else "",
                percentage
            ])

    print("\nResult Exported Successfully.")
    print(f"File: {filename}")

def delete_subject():
    student_id = get_student_id()

    if not student_id:
        print("Student Profile Not Found.")
        return

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, subject_name
        FROM subjects
        WHERE student_id = ?
        ORDER BY subject_name
        """,
        (student_id,)
    )

    subjects = cursor.fetchall()

    if not subjects:
        print("No Subjects Found.")
        connection.close()
        return

    print("\n========================")
    print("DELETE SUBJECT")
    print("========================")

    for i, subject in enumerate(subjects, start=1):
        print(f"{i}. {subject[1]}")

    print(f"{len(subjects) + 1}. Back")

    try:
        choice = int(input("Select Subject: "))
    except ValueError:
        print("Please enter a number.")
        connection.close()
        return

    if choice == len(subjects) + 1:
        connection.close()
        return

    if choice < 1 or choice > len(subjects):
        print("Invalid Choice.")
        connection.close()
        return

    selected_subject = subjects[choice - 1]

    confirmation = input(
        f"Delete '{selected_subject[1]}'? (yes/no): "
    ).strip().lower()

    if confirmation != "yes":
        print("Deletion Cancelled.")
        connection.close()
        return

    cursor.execute(
        """
        DELETE FROM marks
        WHERE student_id = ?
        AND subject_id = ?
        """,
        (student_id, selected_subject[0])
    )

    cursor.execute(
        """
        DELETE FROM subjects
        WHERE id = ?
        AND student_id = ?
        """,
        (selected_subject[0], student_id)
    )

    connection.commit()
    connection.close()

    print("Subject Deleted Successfully.")

def mark_attendance():
    if not require_role("teacher", "admin"):
        return
    print("\n========================")
    print("SELECT STUDENT")
    print("========================")

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            roll_number,
            name,
            class_name
        FROM students
        ORDER BY roll_number
        """
    )

    students = cursor.fetchall()
    connection.close()

    if not students:
        print("No Students Found.")
        return

    for i, student in enumerate(students, start=1):
        print(
            f"{i}. Roll No: {student[1]} | "
            f"Name: {student[2]} | "
            f"Class: {student[3]}"
        )

    print(f"{len(students) + 1}. Back")

    while True:
        try:
            choice = int(
                input("\nSelect Student: ")
            )
        except ValueError:
            print("Please enter a number.")
            continue

        if choice == len(students) + 1:
            return

        if choice < 1 or choice > len(students):
            print("Invalid Choice.")
            continue

        break

    selected_student = students[choice - 1]
    student_id = selected_student[0]

    print("\n========================")
    print("ATTENDANCE")
    print("========================")
    print(f"Roll Number : {selected_student[1]}")
    print(f"Name        : {selected_student[2]}")
    print(f"Class       : {selected_student[3]}")

    attendance_date = input(
        "\nEnter Date (YYYY-MM-DD): "
    ).strip()

    try:
        datetime.strptime(
            attendance_date,
            "%Y-%m-%d"
        )
    except ValueError:
        print("Invalid date format.")
        return

    while True:
        print("\n1. Present")
        print("2. Absent")
        print("3. Back")

        status_choice = input(
            "Enter Choice: "
        ).strip()

        if status_choice == "1":
            status = "Present"
            break

        elif status_choice == "2":
            status = "Absent"
            break

        elif status_choice == "3":
            return

        else:
            print("Invalid Choice.")

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT OR REPLACE INTO attendance
        (
            student_id,
            attendance_date,
            status
        )
        VALUES
        (?,?,?)
        """,
        (
            student_id,
            attendance_date,
            status
        )
    )

    connection.commit()
    connection.close()

    print(
        f"\nAttendance Saved Successfully."
    )
    print(
        f"Student: {selected_student[2]}"
    )
    print(
        f"Date: {attendance_date}"
    )
    print(
        f"Status: {status}"
    )
    log_activity(
        "ATTENDANCE_UPDATED",
        "Attendance record updated."
    )

def view_attendance():
    student_id = get_student_id()

    if not student_id:
        print("Student Profile Not Found.")
        return

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT attendance_date, status
        FROM attendance
        WHERE student_id = ?
        ORDER BY attendance_date DESC
        """,
        (student_id,)
    )

    records = cursor.fetchall()
    connection.close()

    if not records:
        print("No Attendance Records Found.")
        return

    total_days = len(records)

    present_days = sum(
        1 for record in records
        if record[1] == "Present"
    )

    absent_days = sum(
        1 for record in records
        if record[1] == "Absent"
    )

    attendance_percentage = (
        present_days / total_days
    ) * 100

    print("\n========================================")
    print("          ATTENDANCE RECORD")
    print("========================================")

    for record in records:
        print(
            f"{record[0]} : {record[1]}"
        )

    print("\n----------------------------------------")
    print("ATTENDANCE ANALYTICS")
    print("----------------------------------------")

    print(f"Total Days   : {total_days}")
    print(f"Present      : {present_days}")
    print(f"Absent       : {absent_days}")
    print(
        f"Percentage   : "
        f"{attendance_percentage:.2f}%"
    )

    print("========================================")
    
def student_dashboard():
    global current_user
    while True:
        print("\n=======================")
        print("STUDENT DASHBOARD")
        print("=======================")
        print("1. View Profile")
        print("2. Update Profile")
        print("3. Add Subjects")
        print("4. Delete Subject")
        print("5. Add Marks")
        print("6. View Result")
        print("7. Change Password")
        print("8. Mark Attendance")
        print("9. View Attendance")
        print("10. Generate PDF Report")
        print("11. Export Result CSV")
        print("12. Logout")
        choice = input("Enter your choice: ")

        if choice == "1":
            view_profile()
        elif choice == "2":
            update_profile()
        elif choice == "3":
            add_subjects()
        elif choice == "4":
            delete_subject()
        elif choice == "5":
            add_marks()
        elif choice == "6":
            view_result()
        elif choice == "7":
            change_password()
        elif choice == "8":
            mark_attendance()
        elif choice == "9":
            view_attendance()
        elif choice == "10":
            generate_student_report()
        elif choice == "11":
            export_result_csv()
        elif choice == "12":
            log_activity("LOGOUT", "User logged out.")
            break
        else:
            print("Invalid Choice.")

def view_all_students():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            students.roll_number,
            students.name,
            students.email,
            students.school,
            students.class_name,
            users.email
        FROM students
        JOIN users
        ON students.user_id = users.id
        ORDER BY students.roll_number
        """
    )

    students = cursor.fetchall()
    if not students:
        print("No Student Found.")
        connection.close()
        return
    print("\n========================")
    print("ALL STUDENTS")
    print("========================")
    for student in students:
        print(f"""
        Roll Num : {student[0]}
        Name     : {student[1]}
        Email    : {student[2]}
        School   : {student[3]}
        Class    : {student[4]}
        Login    : {student[5]}
        ------------------------------
        """)
    connection.close()

def search_student():
    print("\n===== SEARCH STUDENT =====")
    print("1. Search by Roll Number")
    print("2. Search by Login Email")
    print("3. Back")

    choice = input("Enter Choice: ").strip()

    if choice == "3":
        return

    if choice == "1":
        roll_number = input("Enter Roll Number: ").strip()

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                students.id,
                students.roll_number,
                students.name,
                students.email,
                students.school,
                students.class_name,
                users.email
            FROM students
            JOIN users
            ON students.user_id = users.id
            WHERE students.roll_number = ?
            """,
            (roll_number,)
        )

    elif choice == "2":
        email = input("Enter Login Email: ").strip()

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                students.id,
                students.roll_number,
                students.name,
                students.email,
                students.school,
                students.class_name,
                users.email
            FROM students
            JOIN users
            ON students.user_id = users.id
            WHERE users.email = ?
            AND users.role = 'student'
            """,
            (email,)
        )

    else:
        print("Invalid Choice.")
        return

    student = cursor.fetchone()

    if not student:
        print("Student Not Found.")
        connection.close()
        return

    student_id = student[0]

    print("\n========================")
    print("STUDENT DETAILS")
    print("========================")
    print(f"Roll Number : {student[1]}")
    print(f"Name        : {student[2]}")
    print(f"Email       : {student[3]}")
    print(f"School      : {student[4]}")
    print(f"Class       : {student[5]}")
    print(f"Login Email : {student[6]}")

    cursor.execute(
        """
        SELECT
            subjects.subject_name,
            marks.obtained_marks,
            marks.total_marks
        FROM subjects
        LEFT JOIN marks
        ON subjects.id = marks.subject_id
        WHERE subjects.student_id = ?
        ORDER BY subjects.subject_name
        """,
        (student_id,)
    )

    records = cursor.fetchall()

    print("\nSubjects / Marks")
    print("------------------------")

    if not records:
        print("No Subjects Found.")
    else:
        for record in records:
            if record[1] is None:
                print(f"{record[0]} : Marks Not Added")
            else:
                print(
                    f"{record[0]} : "
                    f"{record[1]:g}/{record[2]:g}"
                )

    connection.close()

def delete_student():
    view_all_students()
    roll_number = input("\nEnter Roll Num to Delete: ")
    confirmation = input(
        "Are you sure you want to delete this student? (yes/no): "
    ).strip().lower()
    if confirmation != "yes":
        print("Deletion Cancelled.")
        return
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, user_id
        FROM students
        WHERE roll_number = ?
        """,
        (roll_number,)
    )

    student = cursor.fetchone()
    if not student:
        print("Student Not Found.")
        connection.close()
        return
    student_id = student[0]
    user_id = student[1]

    cursor.execute(
        "DELETE FROM marks WHERE student_id = ?",
        (student_id,)
    )

    cursor.execute(
        "DELETE FROM subjects WHERE student_id = ?",
        (student_id,)
    )

    cursor.execute(
        "DELETE FROM students WHERE id = ?",
        (student_id,)
    )

    cursor.execute(
        "DELETE FROM users WHERE id = ?",
        (user_id,)
    )

    connection.commit()
    connection.close()

    print("Student Deleted Successfully.")
    log_activity(
        "STUDENT_DELETED",
        f"Student with roll number {roll_number} was deleted."
    )

def reset_student_password():
    email = input("Enter Student Login Email: ").strip()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id
        FROM users
        WHERE email = ?
        AND role = 'student'
        """,
        (email,)
    )

    student = cursor.fetchone()

    if not student:
        print("Student Not Found.")
        connection.close()
        return

    connection.close()

    while True:
        new_password = input("Enter New Password: ")

        if validate_password(new_password):
            break

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
            student[0]
        )
    )

    connection.commit()
    connection.close()

    print("Password Reset Successfully.")
    log_activity(
        "PASSWORD_RESET",
        f"Password reset for student login: {email}"
    )

def view_all_results():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            students.id,
            students.roll_number,
            students.name,
            subjects.subject_name,
            marks.obtained_marks,
            marks.total_marks
        FROM marks
        JOIN students
        ON marks.student_id = students.id
        JOIN subjects
        ON marks.subject_id = subjects.id
        ORDER BY students.roll_number, subjects.subject_name
        """
    )

    results = cursor.fetchall()

    if not results:
        print("No Results Found.")
        connection.close()
        return

    student_results = {}

    for row in results:
        student_id = row[0]

        if student_id not in student_results:
            student_results[student_id] = {
                "roll_number": row[1],
                "name": row[2],
                "subjects": [],
                "total_obtained": 0,
                "total_marks": 0
            }

        student_results[student_id]["subjects"].append(
            (
                row[3],
                row[4],
                row[5]
            )
        )

        student_results[student_id]["total_obtained"] += row[4]
        student_results[student_id]["total_marks"] += row[5]

    student_analytics = []

    for student in student_results.values():

        percentage = (
            student["total_obtained"]
            / student["total_marks"]
        ) * 100

        failed_subjects = []

        for subject in student["subjects"]:
            subject_percentage = (
                subject[1] / subject[2]
            ) * 100

            if subject_percentage < PASS_MARKS_PERCENTAGE:
                failed_subjects.append(subject[0])

        if failed_subjects:
            status = "REAPPEAR"
        elif percentage >= PASS_MARKS_PERCENTAGE:
            status = "PASS"
        else:
            status = "FAIL"

        student_analytics.append(
            {
                "roll_number": student["roll_number"],
                "name": student["name"],
                "percentage": percentage,
                "status": status,
                "failed_subjects": failed_subjects
            }
        )

    total_students = len(student_analytics)

    pass_count = sum(
        1 for student in student_analytics
        if student["status"] == "PASS"
    )

    fail_count = sum(
        1 for student in student_analytics
        if student["status"] == "FAIL"
    )

    reappear_count = sum(
        1 for student in student_analytics
        if student["status"] == "REAPPEAR"
    )

    average_percentage = sum(
        student["percentage"]
        for student in student_analytics
    ) / total_students

    highest_student = max(
        student_analytics,
        key=lambda student: student["percentage"]
    )

    lowest_student = min(
        student_analytics,
        key=lambda student: student["percentage"]
    )

    print("\n========================================")
    print("        ADMIN RESULT ANALYTICS")
    print("========================================")

    print(f"Students With Results : {total_students}")
    print(f"Average Percentage    : {average_percentage:.2f}%")
    print(f"Pass                  : {pass_count}")
    print(f"Fail                  : {fail_count}")
    print(f"Reappear              : {reappear_count}")

    print("\n----------------------------------------")
    print("HIGHEST PERFORMER")
    print("----------------------------------------")

    print(
        f"Roll Number : {highest_student['roll_number']}"
    )
    print(
        f"Name        : {highest_student['name']}"
    )
    print(
        f"Percentage  : {highest_student['percentage']:.2f}%"
    )

    print("\n----------------------------------------")
    print("LOWEST PERFORMER")
    print("----------------------------------------")

    print(
        f"Roll Number : {lowest_student['roll_number']}"
    )
    print(
        f"Name        : {lowest_student['name']}"
    )
    print(
        f"Percentage  : {lowest_student['percentage']:.2f}%"
    )

    print("\n----------------------------------------")
    print("STUDENT RESULT SUMMARY")
    print("----------------------------------------")

    for student in student_analytics:

        print(
            f"{student['roll_number']} | "
            f"{student['name']} | "
            f"{student['percentage']:.2f}% | "
            f"{student['status']}"
        )

        if student["failed_subjects"]:
            print(
                "  Failed: "
                + ", ".join(student["failed_subjects"])
            )

    print("========================================")

    connection.close()

import csv

def export_results_csv():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            students.roll_number,
            students.name,
            subjects.subject_name,
            marks.obtained_marks,
            marks.total_marks
        FROM marks
        JOIN students
        ON marks.student_id = students.id
        JOIN subjects
        ON marks.subject_id = subjects.id
        ORDER BY students.roll_number, subjects.subject_name
        """
    )

    results = cursor.fetchall()
    connection.close()

    if not results:
        print("No Results Found.")
        return

    filename = "student_results.csv"

    with open(
        filename,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "Roll Number",
            "Student Name",
            "Subject",
            "Obtained Marks",
            "Total Marks",
            "Percentage"
        ])

        for row in results:

            percentage = (
                row[3] / row[4]
            ) * 100

            writer.writerow([
                row[0],
                row[1],
                row[2],
                row[3],
                row[4],
                f"{percentage:.2f}%"
            ])

    print(
        f"Results exported successfully to "
        f"{filename}"
    )

def export_result_pdf():
    student_id = get_student_id()

    if not student_id:
        print("Student Profile Not Found.")
        return

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            students.roll_number,
            students.name,
            students.email,
            subjects.subject_name,
            marks.obtained_marks,
            marks.total_marks
        FROM students
        JOIN subjects
        ON students.id = subjects.student_id
        LEFT JOIN marks
        ON subjects.id = marks.subject_id
        AND marks.student_id = students.id
        WHERE students.id = ?
        ORDER BY subjects.subject_name
        """,
        (student_id,)
    )

    result = cursor.fetchall()
    connection.close()

    if not result:
        print("No Result Found.")
        return

    roll_number = result[0][0]
    name = result[0][1]

    filename = f"student_result_{roll_number}.pdf"

    pdf = canvas.Canvas(filename, pagesize=A4)

    width, height = A4

    y = height - 50

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(50, y, "STUDENT RESULT REPORT")

    y -= 40

    pdf.setFont("Helvetica", 11)
    pdf.drawString(50, y, f"Roll Number: {roll_number}")

    y -= 20
    pdf.drawString(50, y, f"Student Name: {name}")

    y -= 35

    pdf.setFont("Helvetica-Bold", 11)

    pdf.drawString(50, y, "Subject")
    pdf.drawString(220, y, "Obtained")
    pdf.drawString(300, y, "Total")
    pdf.drawString(370, y, "Percentage")

    y -= 20

    pdf.setFont("Helvetica", 10)

    for row in result:

        subject = row[3]
        obtained = row[4]
        total = row[5]

        if obtained is None or total is None:
            obtained_text = "N/A"
            total_text = "N/A"
            percentage = "N/A"
        else:
            obtained_text = f"{obtained:.0f}"
            total_text = f"{total:.0f}"
            percentage = f"{(obtained / total) * 100:.2f}%"

        pdf.drawString(50, y, subject)
        pdf.drawString(220, y, obtained_text)
        pdf.drawString(300, y, total_text)
        pdf.drawString(370, y, percentage)

        y -= 20

        if y < 50:
            pdf.showPage()
            y = height - 50
            pdf.setFont("Helvetica", 10)

    pdf.save()

    log_activity(
        "PDF_EXPORT",
        f"Result PDF exported for roll number {roll_number}."
    )

    print("\nPDF Exported Successfully.")
    print(f"File: {filename}")

def student_leaderboard():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            students.id,
            students.roll_number,
            students.name,
            marks.obtained_marks,
            marks.total_marks
        FROM students
        JOIN marks
        ON students.id = marks.student_id
        """
    )

    records = cursor.fetchall()
    connection.close()

    if not records:
        print("No Student Results Found.")
        return

    students = {}

    for record in records:

        student_id = record[0]
        roll_number = record[1]
        name = record[2]
        obtained = record[3]
        total = record[4]

        if student_id not in students:
            students[student_id] = {
                "roll_number": roll_number,
                "name": name,
                "obtained": 0,
                "total": 0
            }

        students[student_id]["obtained"] += obtained
        students[student_id]["total"] += total

    leaderboard = []

    for student in students.values():

        if student["total"] == 0:
            continue

        percentage = (
            student["obtained"]
            / student["total"]
        ) * 100

        leaderboard.append(
            {
                "roll_number": student["roll_number"],
                "name": student["name"],
                "percentage": percentage
            }
        )

    leaderboard.sort(
        key=lambda student: student["percentage"],
        reverse=True
    )

    print("\n========================================")
    print("          STUDENT LEADERBOARD")
    print("========================================")

    print(
        f"{'Rank':<8}"
        f"{'Roll Number':<15}"
        f"{'Name':<25}"
        f"{'Percentage':>12}"
    )

    print("----------------------------------------")

    for rank, student in enumerate(
        leaderboard,
        start=1
    ):

        print(
            f"{rank:<8}"
            f"{student['roll_number']:<15}"
            f"{student['name']:<25}"
            f"{student['percentage']:>10.2f}%"
        )

    print("========================================")

def performance_analytics():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            subjects.subject_name,
            marks.obtained_marks,
            marks.total_marks
        FROM marks
        JOIN subjects
        ON marks.subject_id = subjects.id
        """
    )

    results = cursor.fetchall()
    connection.close()

    if not results:
        print("No Marks Data Found.")
        return

    subject_data = {}

    for subject_name, obtained, total in results:

        if subject_name not in subject_data:
            subject_data[subject_name] = {
                "obtained": 0,
                "total": 0,
                "students": 0
            }

        subject_data[subject_name]["obtained"] += obtained
        subject_data[subject_name]["total"] += total
        subject_data[subject_name]["students"] += 1

    print("\n========================================")
    print("       PERFORMANCE ANALYTICS")
    print("========================================")

    for subject, data in sorted(subject_data.items()):

        percentage = (
            data["obtained"] / data["total"]
        ) * 100

        print(
            f"{subject:20} "
            f"{percentage:.2f}% "
            f"({data['students']} students)"
        )

    print("\n----------------------------------------")
    print("SUBJECT PERFORMANCE")
    print("----------------------------------------")

    highest_subject = max(
        subject_data.items(),
        key=lambda item: (
            item[1]["obtained"] / item[1]["total"]
        )
    )

    lowest_subject = min(
        subject_data.items(),
        key=lambda item: (
            item[1]["obtained"] / item[1]["total"]
        )
    )

    highest_percentage = (
        highest_subject[1]["obtained"]
        / highest_subject[1]["total"]
    ) * 100

    lowest_percentage = (
        lowest_subject[1]["obtained"]
        / lowest_subject[1]["total"]
    ) * 100

    print(
        f"Best Subject   : "
        f"{highest_subject[0]} "
        f"({highest_percentage:.2f}%)"
    )

    print(
        f"Weakest Subject: "
        f"{lowest_subject[0]} "
        f"({lowest_percentage:.2f}%)"
    )

    print("========================================")

def generate_student_report():
    student_id = get_student_id()

    if not student_id:
        print("Student Profile Not Found.")
        return

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            roll_number,
            name,
            email,
            school,
            class_name
        FROM students
        WHERE id = ?
        """,
        (student_id,)
    )

    student = cursor.fetchone()

    if not student:
        print("Student Profile Not Found.")
        connection.close()
        return

    cursor.execute(
        """
        SELECT
            subjects.subject_name,
            marks.obtained_marks,
            marks.total_marks
        FROM subjects
        LEFT JOIN marks
        ON subjects.id = marks.subject_id
        AND marks.student_id = ?
        WHERE subjects.student_id = ?
        ORDER BY subjects.subject_name
        """,
        (student_id, student_id)
    )

    results = cursor.fetchall()

    connection.close()

    if not results:
        print("No Subjects Found.")
        return

    total_obtained = 0
    total_marks = 0

    for subject in results:

        if subject[1] is not None:
            total_obtained += subject[1]
            total_marks += subject[2]

    if total_marks == 0:
        print("Marks are not added yet.")
        return

    percentage = (
        total_obtained / total_marks
    ) * 100

    if percentage >= 90:
        grade = "A+"
    elif percentage >= 80:
        grade = "A"
    elif percentage >= 70:
        grade = "B"
    elif percentage >= 60:
        grade = "C"
    elif percentage >= 50:
        grade = "D"
    elif percentage >= PASS_MARKS_PERCENTAGE:
        grade = "E"
    else:
        grade = "F"

    file_name = (
        f"student_report_{student[0]}.pdf"
    )

    pdf = canvas.Canvas(
        file_name,
        pagesize=A4
    )

    width, height = A4

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawCentredString(
        width / 2,
        height - 60,
        "STUDENT RESULT REPORT"
    )

    pdf.setFont("Helvetica", 11)

    y = height - 100
    pdf.drawString(
        50, y,
        f"Roll Number: {student[0]}"
    )
    y -= 20
    pdf.drawString(
        50, y,
        f"Name: {student[1]}"
    )
    y -= 20
    pdf.drawString(
        50, y,
        f"Email: {student[2]}"
    )
    y -= 20
    pdf.drawString(
        50, y,
        f"School: {student[3]}"
    )
    y -= 20
    pdf.drawString(
        50, y,
        f"Class: {student[4]}"
    )
    y -= 40
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(50, y, "Subject")
    pdf.drawString(250, y, "Obtained")
    pdf.drawString(330, y, "Total")
    pdf.drawString(400, y, "Percentage")
    y -= 20
    pdf.setFont("Helvetica", 10)

    for subject in results:

        subject_name = subject[0]
        obtained = subject[1]
        total = subject[2]

        pdf.drawString(
            50,
            y,
            subject_name
        )

        if obtained is None:
            pdf.drawString(
                250,
                y,
                "Not Added"
            )
        else:
            subject_percentage = (
                obtained / total
            ) * 100

            pdf.drawString(
                250,
                y,
                f"{obtained:.0f}"
            )

            pdf.drawString(
                330,
                y,
                f"{total:.0f}"
            )

            pdf.drawString(
                400,
                y,
                f"{subject_percentage:.2f}%"
            )
        y -= 20
    y -= 20
    pdf.setFont("Helvetica-Bold", 11)

    pdf.drawString(
        50,
        y,
        f"Total Marks: {total_marks:.0f}"
    )
    y -= 20
    pdf.drawString(
        50,
        y,
        f"Obtained Marks: {total_obtained:.0f}"
    )
    y -= 20
    pdf.drawString(
        50,
        y,
        f"Overall Percentage: {percentage:.2f}%"
    )
    y -= 20
    pdf.drawString(
        50,
        y,
        f"Grade: {grade}"
    )

    pdf.save()

    print(
        f"\nPDF Report Generated Successfully: "
        f"{file_name}"
    )

def teacher_dashboard():
    if not require_role("teacher", "admin"):
        return
    global current_user

    while True:
        print("\n=======================")
        print("TEACHER DASHBOARD")
        print("=======================")
        print("1. View Students")
        print("2. Search Student")
        print("3. Add / Update Marks")
        print("4. Mark Attendance")
        print("5. View Results")
        print("6. Logout")

        choice = input("Enter Choice: ").strip()

        if choice == "1":
            view_all_students()

        elif choice == "2":
            search_student()

        elif choice == "3":
            add_marks()

        elif choice == "4":
            mark_attendance()

        elif choice == "5":
            view_all_results()

        elif choice == "6":
            print("Teacher Logged Out.")
            log_activity("LOGOUT", "User logged out.")
            break

        else:
            print("Invalid Choice.")

def view_activity_logs():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            activity_type,
            description,
            created_at
        FROM activity_logs
        ORDER BY id DESC
        """
    )

    logs = cursor.fetchall()
    connection.close()

    if not logs:
        print("\nNo Activity Logs Found.")
        return

    print("\n========================================")
    print("           ACTIVITY LOGS")
    print("========================================")

    for log in logs:
        print(
            f"\n[{log[2]}] "
            f"{log[0]}"
        )
        print(f"Description: {log[1]}")

    print("\n========================================")

def admin_dashboard():
    if not require_role("admin"):
        return
    while True:
        print("\n=======================")
        print("ADMIN DASHBOARD")
        print("=======================")
        print("1. View All Students")
        print("2. Search Student")
        print("3. Delete Student")
        print("4. Reset Student Password.")
        print("5. View All Result")
        print("6. Export Result CSV")
        print("7. Performance Analytics")
        print("8. Student Leaderboard")
        print("9. View Activity Logs")
        print("10. Logout")
        choice = input("Enter Choice: ")
        if choice == "1":
            view_all_students()
        elif choice == "2":
            search_student()
        elif choice == "3":
            delete_student()
        elif choice == "4":
            reset_student_password()
        elif choice == "5":
            view_all_results()
        elif choice == "6":
            export_result_csv()
        elif choice == "7":
            performance_analytics()
        elif choice == "8":
            student_leaderboard()
        elif choice == "9":
            view_activity_logs()
        elif choice == "10":
            log_activity("LOGOUT", "User logged out.")
            break
        else:
            print("Invalid Choice.")
        

def main_menu():
    while True:
        print("\n====================")
        print("STUDENT GRADE TRACKER")
        print("====================")
        print("1. Signup")
        print("2. Login")
        print("3. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            signup()
        elif choice == "2":
            login()
        elif choice == "3":
            print("Good Bye")
            break
        else:
            print("Invalid Choice.")

main_menu()