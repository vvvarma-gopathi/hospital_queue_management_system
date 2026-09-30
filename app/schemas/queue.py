from datetime import datetime
from pydantic import BaseModel


class QueueEntryResponse(BaseModel):
    id: int
    appointment_id: int | None
    patient_id: int
    doctor_id: int
    queue_number: int
    status: str
    arrival_time: datetime


class WaitTimeResponse(BaseModel):
    doctor_id: int
    queue_number: int
    estimated_wait_minutes: int
