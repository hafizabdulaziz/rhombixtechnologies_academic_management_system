from datetime import datetime
from database import get_connection
import session

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
            session.current_user,
            action,
            details,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    )

    connection.commit()
    connection.close()

def view_activity_logs():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            action,
            details,
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
        print(f"Details: {log[1]}")

    print("\n========================================")
