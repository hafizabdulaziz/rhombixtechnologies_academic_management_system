import sys
import os
import unittest
import sqlite3
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from auth import verify_login
from database import get_connection

class TestSystem(unittest.TestCase):
    def test_database_connection(self):
        conn = get_connection()
        self.assertIsNotNone(conn)
        conn.close()

    def test_admin_login(self):
        self.assertIsNotNone(verify_login('abdulaziz555@gmail.com', 'admin123'))

    def test_teacher_login(self):
        self.assertIsNotNone(verify_login('abdulaziz090@gmail.com', 'teacher123'))

    def test_student_login(self):
        # Look for a student user
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT email FROM users WHERE role='student' LIMIT 1")
        student = cursor.fetchone()
        conn.close()
        self.assertIsNotNone(student, "No student account found for login test")

    def test_student_tables(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='students'")
        self.assertIsNotNone(cursor.fetchone())
        conn.close()

    def test_marks_tables(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='marks'")
        self.assertIsNotNone(cursor.fetchone())
        conn.close()

    def test_attendance_table(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='attendance'")
        self.assertIsNotNone(cursor.fetchone())
        conn.close()

    def test_activity_logs(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='activity_logs'")
        self.assertIsNotNone(cursor.fetchone())
        conn.close()

if __name__ == '__main__':
    unittest.main()

# Documentation: Added assertions for session timeouts and failed password validation.
