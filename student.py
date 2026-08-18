from database import get_connection
import session
from activity_logs import log_activity
import marks
import results
import attendance
import exports
import auth
import re

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

def is_valid_roll(roll):
    # Only allow alphanumeric characters
    return bool(re.match('^[a-zA-Z0-9]+$', roll))

def create_student_profile():
    while True:
        roll_number = input("Enter Roll Number: ").strip()

        if not roll_number:
            print("Roll Number cannot be empty.")
            continue
            
        if not is_valid_roll(roll_number):
            print("Roll Number can only contain letters and numbers.")
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
            session.current_user,
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
        (session.current_user,)
    ) 

    student = cursor.fetchone()
    connection.close()
    if not student:
        return None
    return student[0]

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
        (session.current_user,)
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
        (session.current_user,)
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
                (name, session.current_user)
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
                (school, session.current_user)
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
                (class_name, session.current_user)
            )

            connection.commit()
            connection.close()

            print("Class Updated Successfully.")

def student_dashboard():
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
            marks.add_subjects()
        elif choice == "4":
            marks.delete_subject()
        elif choice == "5":
            marks.add_marks()
        elif choice == "6":
            results.view_result()
        elif choice == "7":
            auth.change_password()
        elif choice == "8":
            attendance.mark_attendance()
        elif choice == "9":
            attendance.view_attendance()
        elif choice == "10":
            exports.generate_student_report()
        elif choice == "11":
            exports.export_result_csv()
        elif choice == "12":
            log_activity("LOGOUT", "User logged out.")
            session.current_user = None
            break
        else:
            print("Invalid Choice.")

# Documentation: Explained dashboard logic, enrollment, and grade calculations.
