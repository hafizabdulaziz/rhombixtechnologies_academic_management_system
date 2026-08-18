# 🎓 Academic Management System (Student Grade Tracker)

```
██████╗  ██████╗  ██████╗ ███╗   ███╗██████╗ ██╗██╗  ██╗
██╔══██╗██╔═══██╗██╔═══██╗████╗ ████║██╔══██╗██║╚██╗██╔╝
██████╔╝██║   ██║██║   ██║██╔████╔██║██████╔╝██║ ╚███╔╝ 
██╔══██╗██║   ██║██║   ██║██║╚██╔╝██║██╔══██╗██║ ██╔██╗ 
██████╔╝╚██████╔╝╚██████╔╝██║ ╚═╝ ██║██████╔╝██║██╔╝ ██╗
╚══════╝  ╚═════╝  ╚═════╝ ╚═╝     ╚═╝╚═════╝ ╚═╝╚═╝  ╚═╝
  A Professional, Modular, and Secure Academic Portal
```

---

## 📖 About the Project

The **Academic Management System (Student Grade Tracker)** is an enterprise-grade, console-based desktop application designed to streamline academic administrative workflows and record-keeping. Developed as a modern restoration of a legacy monolithic system, this platform provides a secure, role-based ecosystem for managing student profiles, grades, attendance, performance analytics, and system audit logs.

### Core Value Proposition
For schools, colleges, and training centers requiring lightweight yet highly secure academic administration, this system offers:
* **Zero Overhead:** A high-performance console interface that requires no heavy web servers or complex browser setups.
* **Granular Role-Based Access Control (RBAC):** Strict boundaries separating Student, Teacher, and Administrator operations.
* **Offline-First Data Integrity:** A robust SQLite storage backend with automatic transaction handling and backup recovery.
* **Compliance & Auditing:** Transparent, tamper-evident activity logging for all administrative actions.
* **Professional Reporting:** Instant, professional PDF grade cards and CSV exports designed for academic distribution.

---

## 🏛️ System Architecture

The application has been engineered following strict **modular programming principles**, separating concerns between the database layer, security, business logic, and presentation menus.

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
         │  (Active User Session)│   │ (SHA-256 Hashing & E2E)│
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
1. **`main.py`**: Boots the system, initializes directories/databases, and handles the main loop.
2. **`auth.py`**: Orchestrates signups, logins, and session handoffs to respective dashboards.
3. **`database.py`**: Manages the SQLite connection pool, schema initialization, and transactional queries.
4. **`session.py`**: Encapsulates state for the currently logged-in user to prevent session hijacking.
5. **`security.py`**: Secures student data using SHA-256 cryptographic hashing and inputs sanitization.
6. **`menus.py`**: Renders clear and structured command-line UI tables, prompts, and options.
7. **`student.py`**: The portal for students to view grades, report cards, logs, and mark attendance.
8. **`teacher.py`**: The interface for educators to manage cohorts, record marks, and view analytics.
9. **`admin.py`**: The administrative console for activity audits, system backup/restore, and user accounts.
10. **`marks.py` / `attendance.py` / `results.py`**: Core domain logic handling grading scales, ratios, and academic calculations.
11. **`exports.py`**: High-performance report rendering utilizing ReportLab canvas and standard CSV formats.

---

## 🚀 Key Features

### 1. Robust Security & RBAC
* **Password Security:** Multi-layered security checking with SHA-256 cryptographic hashing. Passwords are never stored in plain text.
* **Dashboard Isolation:** Users are strictly confined to their authorized dashboards. Any lateral movement attempts are instantly blocked and logged.

### 2. Live Academic Portals
* **Student View:** Self-service portal where students can check their grades, view overall GPA/percentages, view daily attendance records, and download official report cards.
* **Teacher View:** Allows teachers to quickly add/update subject marks, log attendance for a class, view student performance metrics, and search records by Roll Number.
* **Admin Control:** Administrators can audit user activity logs, add/remove system users, change roles, and perform safe database operations (Backups & Restores).

### 3. Analytics & Automated Reports
* **Automatic Grading:** Computes custom percentages and assigns grades (A+, A, B, C, F) dynamically.
* **PDF Report Cards:** Generates professional, ready-to-print PDF report cards using programmatic ReportLab drawing canvases complete with metadata, header tables, and grade summaries.
* **CSV Export:** Support for mass data exporting of class rosters and marks for further external processing (e.g., in Excel).

---

## 🛠️ The Restoration & Development Journey

This repository represents a complete refactoring and optimization of a legacy monolithic script (`student_grade_tracker_original.py`). During the development and migration process, several critical technical issues were resolved:

### 🧩 1. Circular Imports Resolution
* **The Issue:** Since the dashboard modules (`student.py`, `teacher.py`, `admin.py`) and the authentication controller (`auth.py`) are highly interdependent, initial designs suffered from circular imports leading to `ImportError`.
* **The Solution:** Applied clean local importing design patterns. Core modules load each other dynamically inside specific functional hooks instead of globally at module load-time, maintaining high modular separation without cyclic dependency locks.

### 💾 2. Windows Path & Roll Number Sanitization
* **The Issue:** Roll numbers in the legacy system could contain slashes or unsafe Windows characters (e.g., `S-2026/01`). When generating CSV or PDF files using these roll numbers as file names, the OS would throw a `FileNotFoundError`.
* **The Solution:** Added a path-sanitizer function in the export pipeline that strips out illegal OS path characters (e.g., converting slashes `/` into hyphens `-`), ensuring reliable file generation on all Windows, macOS, and Linux environments.

### 🔐 3. Strict Permission Parity
* **The Issue:** Auditing the legacy code revealed permission gaps where students could theoretically access backend grading calculation routines.
* **The Solution:** Restored strict permission checks across all API layers. The business modules (`marks.py`, `attendance.py`, `results.py`) actively verify user session roles before executing database modifications.

---

## 💾 Database Schema

The database relies on a highly normalized SQLite relational structure:

```
┌─────────────────────────────────┐        ┌─────────────────────────────────┐
│              users              │        │            subjects             │
├─────────────────────────────────┤        ├─────────────────────────────────┤
│ PK  username      VARCHAR(50)   │◄──────┐│ PK  subject_code  VARCHAR(10)   │
│     password      VARCHAR(64)   │       ││     subject_name  VARCHAR(100)  │
│     role          VARCHAR(10)   │       │└─────────────────────────────────┘
└─────────────────────────────────┘       │                 ▲
                                          │                 │
┌─────────────────────────────────┐       │                 │
│            students             │       │                 │
├─────────────────────────────────┤       │                 │
│ PK  roll_no       VARCHAR(20)   │◄────┐ │                 │
│ FK  username      VARCHAR(50)   │     │ │                 │
│     name          VARCHAR(100)  │     │ │                 │
│     class         VARCHAR(20)   │     │ │                 │
└─────────────────────────────────┘     │ │                 │
                                        │ │                 │
┌─────────────────────────────────┐     │ │        ┌────────┴────────────────────────┐
│            attendance           │     │ │        │              marks              │
├─────────────────────────────────┤     │ │        ├─────────────────────────────────┤
│ PK  attendance_id INTEGER (AUTO)│     │ │        │ PK  mark_id      INTEGER (AUTO) │
│ FK  roll_no       VARCHAR(20)   ├───┐ │ │        │ FK  roll_no      VARCHAR(20)    ├─┘
│     date          DATE          │   │ │ │        │ FK  subject_code VARCHAR(10)    │
│     status        VARCHAR(10)   │   │ │ │        │     marks_obtained REAL         │
└─────────────────────────────────┘   │ │ │        │     max_marks      REAL         │
                                      │ │ │        └─────────────────────────────────┘
                                      │ │ │
┌─────────────────────────────────┐   │ │ │
│          activity_logs          │   │ │ │
├─────────────────────────────────┤   │ │ │
│ PK  log_id        INTEGER (AUTO)│   │ │ │
│     username      VARCHAR(50)   │   │ │ │
│     action        TEXT          │   │ │ │
│     timestamp     DATETIME      │   │ │ │
└─────────────────────────────────┘   │ │ │
                                      │ │ │
                                      │ │ │
                                      ▼ ▼ │
                       ┌──────────────────┴──────────────┐
                       │          student_subjects       │
                       ├─────────────────────────────────┤
                       │ PK, FK1  roll_no   VARCHAR(20)  │
                       │ PK, FK2  sub_code  VARCHAR(10)  │
                       └─────────────────────────────────┘
```

---

## ⚙️ Installation & Requirements

### System Requirements
* **Python Version:** Python 3.12 or newer.
* **OS Support:** Windows 10/11, macOS 13+, Linux (Ubuntu/Debian recommended).

### Installation Instructions
1. **Clone the Repository:**
   ```bash
   git clone https://github.com/hafizabdulaziz/rhombixtechnologies_academic_management_system.git
   cd rhombixtechnologies_academic_management_system
   ```

2. **Set up a Virtual Environment (Optional but Recommended):**
   ```bash
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On macOS/Linux:
   source .venv/bin/activate
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

### Default Login Accounts for Testing
* **System Administrator:**
  * **Username:** `admin`
  * **Password:** `admin123`
* **Teacher Portal:**
  * **Username:** `teacher`
  * **Password:** `teacher123`

### Main Operations Checklist
* **As Admin:** 
  1. Add new courses and student accounts.
  2. View complete system-wide log tracks to audit behavior.
  3. Perform database operations (back up the core database structure).
* **As Teacher:**
  1. Record subject marks for specific students.
  2. Log daily attendance checklists.
  3. Audit class average percentages.
* **As Student:**
  1. Register for courses.
  2. Record attendance self-reports.
  3. View official result score cards and download professional PDFs.

---

## 🧪 Verification & Testing Suite

We maintain standard automated unit and integration tests under the `tests/` directory.

To run the automated test suite and ensure complete system integrity:
```bash
python -m unittest tests/test_system.py
```

### Coverage Scope:
* Database Connection & Table Schema Integrity.
* User Account Registration & Hashing validation.
* Session Initialization and Expiry hooks.
* Grade thresholds, percentage calculators, and GPAs.
* CSV Parsing and PDF generation pipelines.

---

## 📜 License & About

This project is open-source and released under the MIT License. Developed and restored with professional software engineering practices by **Hafiz Abdul Aziz** at Panaversity.
