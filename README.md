# Healthcare Appointment & Queue Management System

Simple FastAPI backend for:

- Admin
- Doctor
- Patient
- Receptionist

## Stack

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- MongoDB
- JWT
- Pytest

## Architecture

Frontend
→ FastAPI routers
→ Authentication/RBAC
→ Services
→ Repositories
→ PostgreSQL

Audit events are stored in MongoDB.

## Run locally

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it and install:

```bash
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and update values if needed.

Start PostgreSQL and MongoDB, then:

```bash
uvicorn app.main:app --reload
```

Open:

http://localhost:8000/docs

## Frontend integration updates

The current backend supports the complete self-registration and live queue hand-off used by the HealthCare frontend.

### Self-registration

- `POST /api/v1/auth/register/patient` creates a PATIENT user and linked patient profile.
- `POST /api/v1/auth/register/doctor` creates a DOCTOR user and linked doctor profile.
- `GET /api/v1/auth/me` returns `profile_id` for patient and doctor accounts.

Admin and receptionist accounts remain admin-managed through `POST /api/v1/admin/users`.

### Appointment -> queue workflow

The intended live workflow is:

```text
Book appointment
      ↓
SCHEDULED
      ↓
Check in
      ↓
CHECKED_IN → queue entry is created automatically
      ↓
WAITING
      ↓
Call next
      ↓
CALLED
      ↓
Start consultation
      ↓
IN_CONSULTATION
      ↓
Complete
      ↓
COMPLETED
```

`POST /api/v1/queue/appointment/{appointment_id}` now requires the appointment to be `CHECKED_IN`, so the normal path is to check in first. The check-in endpoint creates the queue entry atomically.

Additional read endpoints used by the frontend:

- `GET /api/v1/appointments/`
- `GET /api/v1/appointments/doctor/{doctor_id}`
- `GET /api/v1/queue/patient/{patient_id}`

### CORS

CORS is controlled through the `CORS_ORIGINS` environment variable as a comma-separated list.

Local development default:

```env
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

For deployment, set it to the exact frontend origin(s), for example:

```env
CORS_ORIGINS=https://your-frontend.example.com
```
