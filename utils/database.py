import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "database" / "attendance.db"


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            course TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            attendance_date TEXT NOT NULL,
            marked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(student_id) REFERENCES students(student_id)
        )
        """
    )
    conn.commit()
    conn.close()


def add_student(student_id, name, course):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO students (student_id, name, course)
        VALUES (?, ?, ?)
        ON CONFLICT(student_id) DO UPDATE SET
            name = excluded.name,
            course = excluded.course
        """,
        (student_id, name, course),
    )
    conn.commit()
    conn.close()


def get_students():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM students ORDER BY name ASC").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def mark_attendance(student_id):
    conn = get_connection()
    cursor = conn.cursor()
    today = __import__("datetime").datetime.now().strftime("%Y-%m-%d")
    existing = cursor.execute(
        "SELECT id FROM attendance WHERE student_id = ? AND attendance_date = ?",
        (student_id, today),
    ).fetchone()

    if existing:
        conn.close()
        return "already_marked"

    cursor.execute(
        "INSERT INTO attendance (student_id, attendance_date) VALUES (?, ?)",
        (student_id, today),
    )
    conn.commit()
    conn.close()
    return "marked"


def get_attendance(limit=100):
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT a.id, a.student_id, s.name, s.course, a.attendance_date, a.marked_at
        FROM attendance a
        JOIN students s ON s.student_id = a.student_id
        ORDER BY a.marked_at DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]
