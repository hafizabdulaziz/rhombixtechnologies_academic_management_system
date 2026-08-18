import sqlite3
conn = sqlite3.connect('student_tracker.db')
cursor = conn.cursor()
cursor.execute("SELECT email FROM users WHERE role='teacher'")
print(cursor.fetchall())
conn.close()
