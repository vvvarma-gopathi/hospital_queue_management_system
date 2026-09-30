from datetime import date, time
from pydantic import BaseModel


class LeaveCreate(BaseModel):
    leave_date: date
    start_time: time | None = None
    end_time: time | None = None
    reason: str | None = None


class LeaveResponse(LeaveCreate):
    id: int
    doctor_id: int
