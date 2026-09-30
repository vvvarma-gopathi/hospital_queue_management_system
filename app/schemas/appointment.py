from datetime import date, time
from pydantic import BaseModel


class AppointmentCreate(BaseModel):
    patient_id: int
    doctor_id: int
    appointment_date: date
    start_time: time
    duration_minutes: int
    reason: str | None = None
    appointment_type: str = "SCHEDULED"


class AppointmentResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    appointment_date: date
    start_time: time
    end_time: time
    duration_minutes: int
    status: str
    appointment_type: str
    reason: str | None
