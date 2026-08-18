from database import get_connection
import config

def view_result():
    from student import get_student_id
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

        if percentage < config.PASS_MARKS_PERCENTAGE:
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
    elif overall_percentage >= config.PASS_MARKS_PERCENTAGE:
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
    elif overall_percentage >= config.PASS_MARKS_PERCENTAGE:
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

            if subject_percentage < config.PASS_MARKS_PERCENTAGE:
                failed_subjects.append(subject[0])

        if failed_subjects:
            status = "REAPPEAR"
        elif percentage >= config.PASS_MARKS_PERCENTAGE:
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
