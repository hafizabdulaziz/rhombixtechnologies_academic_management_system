# Academic Management System (Student Grade Tracker)

A modular, console-based academic management and grade tracking application implemented in Python and SQLite.

## Overview

The Academic Management System provides academic record-keeping, grade tracking, attendance management, performance analytics, and system audit logging through an interactive terminal interface. Refactored from a legacy monolithic implementation (`student_grade_tracker_original.py`), the codebase follows a decoupled modular architecture with clear separation of concerns across authentication, database persistence, domain logic, and presentation menus.

## Key Capabilities

- **Role-Based Access Control (RBAC)**: Enforces role boundaries across Student, Teacher, and Administrator personas.
- **Relational Persistence**: Uses SQLite with transactional operations for structured record storage.
- **Audit Logging**: Logs administrative events and state modifications for tracking and traceability.
- **Academic Reporting**: Generates formatted PDF grade report cards using ReportLab alongside CSV export pipelines.
- **Zero Heavyweight Dependencies**: Runs entirely in console environments without requiring browser frontends or external application servers.

## System Architecture

```text
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

| Module | Responsibility |
| :--- | :--- |
| **`main.py`** | Application bootstrap and top-level execution loop |
| **`auth.py`** | Registration, login authentication, and session handoffs |
| **`session.py`** | Session state management for the currently authenticated user |
| **`security.py`** | Credential security and password hashing routines |
| **`database.py`** | SQLite database schema initialization and connection management |
| **`menus.py`** | Terminal UI formatting, banners, and navigational prompts |
| **`student.py`** | Student portal operations |
| **`teacher.py`** | Teacher evaluation and grading interface |
| **`admin.py`** | Administrative console, student records, and system settings |
| **`marks.py` / `attendance.py` / `results.py`** | Domain business logic, percentage calculations, and attendance tracking |
| **`exports.py`** | Report generation engine for PDF and CSV output formats |

## Functional Portals & Features

### Role-Based Portals
- **Student Portal**:
  - View and update profile information.
  - Enroll and remove subject selections.
  - Review academic evaluation results and attendance records.
  - Update account passwords.
  - Generate ReportLab PDF grade reports and export CSV results.
  - *Note: While menu options for "Add Marks" and "Mark Attendance" appear in the menu layout, execution is restricted to authorized roles and blocked for student accounts.*
- **Teacher Portal**:
  - Search and inspect student academic profiles.
  - Input and modify subject marks.
  - Record attendance entries.
  - Review student aggregate performance.
- **Administrator Console**:
  - Comprehensive student CRUD and password reset utilities.
  - Academic result aggregation and performance analytics.
  - Academic leaderboards and cohort performance summaries.
  - System activity and audit log inspection.
  - Cohort CSV export generation.

### Analytics & Reporting Engine
- **Automated Grading Engine**: Computes overall percentage scores and evaluates letter grades dynamically (`A+`, `A`, `B`, `C`, `F`).
- **PDF Generation**: Renders formatted grade cards via ReportLab.
- **CSV Data Pipelines**: Exports student rosters, marks, and historical results for external tools.

## Architectural Refactoring Notes

The codebase refactored an unorganized legacy script (`student_grade_tracker_original.py`), resolving several specific architectural challenges:
1. **Circular Import Resolution**: Addressed interdependent module imports by scoping imports locally within functional hooks, preserving module isolation.
2. **File Path Sanitization**: Implemented roll number sanitization in export workflows to ensure cross-platform file path compatibility.
3. **Permission Parity**: Rebuilt authorization validation across all operations to prevent privilege escalation.

## Database Schema

The SQLite schema consists of relational entities:
- `users`: User identity and role associations.
- `students`: Core student demographic profiles.
- `subjects`: Academic course offerings.
- `student_subjects`: Student-course enrollment relationships.
- `marks`: Academic score entries linked to students and subjects.
- `attendance`: Date-stamped attendance logs.
- `activity_logs`: Administrative actions and state changes.

## Setup & Execution

### Prerequisites
- Python 3.12 or newer
- Operating System: Windows 10/11, macOS, or Linux

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/hafizabdulaziz/rhombixtechnologies_academic_management_system.git
   cd rhombixtechnologies_academic_management_system
   ```

2. **Configure Virtual Environment**:
   ```bash
   python -m venv .venv

   # Windows
   .venv\Scripts\activate

   # Linux / macOS
   source .venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch Application**:
   ```bash
   python main.py
   ```

### Demonstration Credentials
*Provided for local functional testing:*
- **Administrator**: `admin` / `admin123`
- **Teacher**: `teacher` / `teacher123`

## Testing & Verification

Automated test specifications are located within the `tests/` directory:

```bash
python -m unittest tests/test_system.py
```
*Current test suite status: 8/8 automated test cases passing across Student, Teacher, and Administrator operational workflows.*

## License

This project is licensed under the MIT License. Developed by Hafiz Abdul Aziz at Panaversity.
