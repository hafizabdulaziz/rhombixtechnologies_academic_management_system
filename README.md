# 🎓 Academic Management System (Student Grade Tracker)

```
██████╗ ██╗  ██╗ ██████╗ ███╗   ███╗██████╗ ██╗██╗  ██╗
██╔══██╗██║  ██║██╔═══██╗████╗ ████║██╔══██╗██║╚██╗██╔╝
██████╔╝███████║██║   ██║██╔████╔██║██████╔╝██║ ╚███╔╝ 
██╔══██╗██╔══██║██║   ██║██║╚██╔╝██║██╔══██╗██║ ██╔██╗ 
██║  ██║██║  ██║╚██████╔╝██║ ╚═╝ ██║██████╔╝██║██╔╝ ██╗
╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝╚═════╝ ╚═╝╚═╝  ╚═╝
  A Professional, Modular Academic Portal
```

---

## 📖 About the Project

The **Academic Management System (Student Grade Tracker)** is a console-based desktop application designed to streamline academic administrative workflows and record-keeping. Developed as a modern restoration of a legacy monolithic system, this platform provides a role-based ecosystem for managing student profiles, grades, attendance, performance analytics, and system audit logs.

### Core Value Proposition
For schools, colleges, and training centers requiring lightweight academic administration, this system offers:
* **Zero Overhead:** A console interface that requires no heavy web servers or complex browser setups.
* **Granular Role-Based Access Control (RBAC):** Distinct boundaries separating Student, Teacher, and Administrator operations.
* **Data Integrity:** A SQLite storage backend with automatic transaction handling.
* **Auditing:** Systematic activity logging for administrative actions.
* **Reporting:** Professional PDF grade cards and CSV exports designed for academic distribution.

---

## 🏛️ System Architecture

The application is engineered following **modular programming principles**, separating concerns between the database layer, security, business logic, and presentation menus.

```
                  ┌─────────────────────────────────┐
                  │             main.py             │
                  │      (Application Entry)        │
                  └────────────────┬────────────────┘
                                   │
                  ┌────────────────▼────────────────┐
                  │             auth.py             │
                  │   (Authentication & Routing)    │
                  └──────┬───────────────────┬──────┘
                         │                   │
         ┌───────────────▼───────┐   ┌───────▼───────────────┐
         │       session.py      │   │       security.py     │
         │  (Active User Session)│   │ (Password Hashing)    │
         └───────────────────────┘   └───────────────────────┘
                                   │
                  ┌────────────────▼────────────────┐
                  │             menus.py            │
                  │   (Terminal UI Presentation)    │
                  └──────┬───────────┬───────────┬──┘
                         │           │           │
         ┌───────────────▼──┐ ┌──────▼──────┐ ┌──▼──────────────┐
         │    student.py    │ │  teacher.py │ │    admin.py     │
         │  (Student Portal)│ │(Teacher Ptl)│ │(Admin Dashboard)│
         └───────┬──────────┘ └──────┬──────┘ └───┬─────────────┘
                 │                   │            │
                 └─────────┬─────────┴────────────┘
                           │
  ┌────────────────────────┼────────────────────────┬────────────────────────┐
  │                        │                        │                        │
┌─▼─────────────┐    ┌─────▼──────────┐       ┌─────▼──────────┐       ┌─────▼──────────┐
│   database.py │    │    marks.py    │       │  attendance.py │       │   results.py   │
│ (SQLite Layer)│    │ (Academic Grd) │       │(Attendance Trk)│       │ (Analytics Eng)│
└───────────────┘    └────────────────┘       └────────────────┘       └────────────────┘
                                                            │
                                                   ┌────────▼──────────┐
                                                   │    exports.py     │
                                                   │ (PDF & CSV Engine)│
                                                   └───────────────────┘
```

### Module Breakdown
1. **`main.py`**: Boots the system and handles the main loop.
2. **`auth.py`**: Orchestrates signups, logins, and session handoffs.
3. **`database.py`**: Manages SQLite connection and schema.
4. **`session.py`**: Encapsulates state for the currently logged-in user.
5. **`security.py`**: Secures student data using cryptographic hashing.
6. **`menus.py`**: Renders clear command-line UI elements.
7. **`student.py`**: Portal for students.
8. **`teacher.py`**: Interface for educators.
9. **`admin.py`**: Administrative console.
10. **`marks.py` / `attendance.py` / `results.py`**: Core domain logic.
11. **`exports.py`**: Report rendering engine.

---

## 🚀 Key Features

### 1. Security & RBAC
* **Password Security:** Cryptographic hashing for user credentials.
* **Dashboard Isolation:** Users are restricted to their authorized dashboards.

### 2. Academic Portals
* **Student View:**
  * View Profile
  * Update Profile
  * Add/Delete Subjects
  * View Results
  * Change Password
  * View Attendance
  * Generate PDF/Export CSV
  * *Note: "Add Marks" and "Mark Attendance" menu options are visible but restricted by role authorization; Student execution is blocked.*
* **Teacher View:**
  * View/Search Students
  * Add/Update Marks
  * Mark Attendance
  * View Results
* **Admin Control:**
  * View/Search/Delete Students
  * Reset Student Password
  * View Results
  * Export Results CSV
  * Performance Analytics
  * Student Leaderboard
  * Activity Logs

### 3. Analytics & Automated Reports
* **Automatic Grading:** Computes percentages and assigns grades (A+, A, B, C, F) dynamically.
* **PDF Report Cards:** Generates professional report cards using ReportLab.
* **CSV Export:** Export class rosters and marks for external processing.

---

## 🛠️ The Restoration & Development Journey

This repository represents a refactoring of a legacy monolithic script (`student_grade_tracker_original.py`). Technical issues resolved include:

### 🧩 1. Circular Imports Resolution
Refactored imports to be local inside functional hooks, maintaining modular separation.

### 💾 2. Roll Number Sanitization
Added a path-sanitizer function in the export pipeline to ensure reliable file generation on all operating systems.

### 🔐 3. Strict Permission Parity
Restored strict permission checks.

---

## 💾 Database Schema

The database utilizes an SQLite relational structure consisting of tables for `users`, `students`, `subjects`, `student_subjects`, `marks`, `attendance`, and `activity_logs`.

---

## ⚙️ Installation & Requirements

### System Requirements
* **Python Version:** Python 3.12 or newer.
* **OS Support:** Windows 10/11, macOS 13+, Linux.

### Installation Instructions
1. **Clone the Repository:**
   ```bash
   git clone https://github.com/hafizabdulaziz/rhombixtechnologies_academic_management_system.git
   cd rhombixtechnologies_academic_management_system
   ```

2. **Set up a Virtual Environment (Recommended):**
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch the Application:**
   ```bash
   python main.py
   ```

---

## 🕹️ Interactive Guide & User Roles

### DEMO/TEST Accounts
*These credentials are for demonstration purposes only and must be changed before deployment.*
* **System Administrator:** `admin` / `admin123`
* **Teacher Portal:** `teacher` / `teacher123`

---

## 🧪 Verification & Testing Suite

Automated unit and integration tests are in the `tests/` directory.

To run tests:
```bash
python -m unittest tests/test_system.py
```
*Current status: 8/8 automated tests passed. Workflows for Student, Teacher, and Admin have been interactively verified.*

---

## 📜 License & About

This project is open-source and released under the MIT License. Developed by **Hafiz Abdul Aziz** at Panaversity.
