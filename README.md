# EWB Student CRUD API

A student record management backend built using Python, FastAPI, and SQLite for the EWB Python Backend Development Internship Project.

## Features

- Create student records
- List and search students by name
- Retrieve a student by ID
- Update student details
- Delete student records
- Input validation and duplicate email handling
- Persistent SQLite database
- Interactive Swagger API documentation

## Technologies

- Python
- FastAPI
- SQLite
- Pydantic
- Uvicorn

## Setup

### 1. Create and activate a virtual environment

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
py -m pip install -r requirements.txt
```

### 3. Run the application

```powershell
py -m uvicorn main:app --reload
```

## API Documentation

After starting the application, open:

http://127.0.0.1:8000/docs

## Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/students` | Create a student |
| GET | `/students` | List students |
| GET | `/students/{student_id}` | Retrieve a student |
| PATCH | `/students/{student_id}` | Update a student |
| DELETE | `/students/{student_id}` | Delete a student |

**Note:** Use fictional student data for testing.
