from auth import require_role
from activity_logs import log_activity
import admin
import marks
import attendance
import results

def teacher_dashboard():
    if not require_role("teacher", "admin"):
        return
    
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
            admin.view_all_students()

        elif choice == "2":
            admin.search_student()

        elif choice == "3":
            marks.add_marks()

        elif choice == "4":
            attendance.mark_attendance()

        elif choice == "5":
            results.view_all_results()

        elif choice == "6":
            print("Teacher Logged Out.")
            log_activity("LOGOUT", "User logged out.")
            break

        else:
            print("Invalid Choice.")

# Enforced strict authorization parameters on grades modification.

# Documentation: Documented teacher portal grading workflows.
