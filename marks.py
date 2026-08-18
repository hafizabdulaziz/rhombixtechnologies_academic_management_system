from database import get_connection
import session
from activity_logs import log_activity
import student

def subjects_already_exist():
    student_id = student.get_student_id()
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
    student_id = student.get_student_id()

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

        except Exception: # Broad catch to be safe for now, as in original
            print(f"{subject_name} Already Exists.")

    connection.commit()
    connection.close()

    print(f"\n{added_count} New Subject(s) Added Successfully.")

def delete_subject():
    student_id = student.get_student_id()

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

def add_marks():
    # This was a shared function in the original, I'll place it here
    # Needs to be restricted by role as in original
    import auth
    if not auth.require_role("teacher", "admin"):
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

# Documentation: Detailed marks parsing, validation, and percentage formulas.
