import csv
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from database import get_connection
from activity_logs import log_activity
import config

def sanitize_filename(name):
    # Replace characters not safe for filenames
    invalid_chars = '\\/:*?"<>|'
    for char in invalid_chars:
        name = name.replace(char, '_')
    return name

def export_result_csv():
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

    sanitized_roll = sanitize_filename(str(result[0][0]))
    filename = f"student_result_{sanitized_roll}.csv"

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

    sanitized_roll = sanitize_filename(str(roll_number))
    filename = f"student_result_{sanitized_roll}.pdf"

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

def generate_student_report():
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
    elif percentage >= config.PASS_MARKS_PERCENTAGE:
        grade = "E"
    else:
        grade = "F"

    sanitized_roll = sanitize_filename(str(student[0]))
    file_name = f"student_report_{sanitized_roll}.pdf"

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

# Added PDF report rendering using ReportLab canvas routines.
