
from contextlib import asynccontextmanager
from datetime import date
import sqlite3

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, EmailStr, Field

DB_NAME = "students.db"


def connect_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with connect_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                dob TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                phone TEXT,
                course TEXT,
                address TEXT
            )
        """)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="EWB Student CRUD API",
    description="Student management using FastAPI and SQLite",
    version="1.0.0",
    lifespan=lifespan,
)


class StudentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    dob: date
    email: EmailStr
    phone: str | None = None
    course: str | None = None
    address: str | None = None


class StudentUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1)
    dob: date | None = None
    email: EmailStr | None = None
    phone: str | None = None
    course: str | None = None
    address: str | None = None


def get_student_or_404(conn, student_id):
    row = conn.execute(
        "SELECT * FROM students WHERE id = ?", (student_id,)
    ).fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="Student not found")

    return dict(row)


@app.get("/")
def home():
    return {"message": "EWB Student CRUD API is running"}


@app.post("/students", status_code=201)
def create_student(student: StudentCreate):
    data = student.model_dump()
    data["dob"] = data["dob"].isoformat()
    data["email"] = str(data["email"])

    try:
        with connect_db() as conn:
            cursor = conn.execute("""
                INSERT INTO students
                (name, dob, email, phone, course, address)
                VALUES (:name, :dob, :email, :phone, :course, :address)
            """, data)

            return get_student_or_404(conn, cursor.lastrowid)

    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Email already exists",
        )


@app.get("/students")
def list_students(
    name: str | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    with connect_db() as conn:
        if name:
            rows = conn.execute("""
                SELECT * FROM students
                WHERE name LIKE ?
                ORDER BY id
                LIMIT ? OFFSET ?
            """, (f"%{name}%", limit, offset)).fetchall()
        else:
            rows = conn.execute("""
                SELECT * FROM students
                ORDER BY id
                LIMIT ? OFFSET ?
            """, (limit, offset)).fetchall()

        return [dict(row) for row in rows]


@app.get("/students/{student_id}")
def get_student(student_id: int):
    with connect_db() as conn:
        return get_student_or_404(conn, student_id)


@app.patch("/students/{student_id}")
def update_student(student_id: int, student: StudentUpdate):
    changes = student.model_dump(exclude_unset=True)

    if not changes:
        raise HTTPException(
            status_code=400, detail="No update fields supplied"
        )

    if any(changes[key] is None for key in ("name", "dob", "email")
           if key in changes):
        raise HTTPException(
            status_code=422,
            detail="Name, DOB and email cannot be null",
        )

    if "dob" in changes:
        changes["dob"] = changes["dob"].isoformat()

    if "email" in changes:
        changes["email"] = str(changes["email"])

    try:
        with connect_db() as conn:
            get_student_or_404(conn, student_id)

            assignments = ", ".join(
                f"{key} = ?" for key in changes
            )
            values = list(changes.values()) + [student_id]

            conn.execute(
                f"UPDATE students SET {assignments} WHERE id = ?",
                values,
            )

            return get_student_or_404(conn, student_id)

    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Email already exists",
        )


@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    with connect_db() as conn:
        get_student_or_404(conn, student_id)
        conn.execute("DELETE FROM students WHERE id = ?", (student_id,))

    return {"message": "Student deleted successfully", "id": student_id}
