from database import get_connection
from activity_logs import log_activity
from datetime import datetime

def mark_attendance():
    from auth import require_role
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
    from student import get_student_id
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

# Documentation: Attendance ratio calculation and status tracking.
