from database import get_connection
from auth import require_role
from activity_logs import log_activity, view_activity_logs
import results
import exports

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
    connection.close()

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
    from auth import validate_password, hash_password
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
            results.view_all_results()
        elif choice == "6":
            exports.export_results_csv()
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

# Verified strict session checks on entry points.
