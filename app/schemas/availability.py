from datetime import time
from pydantic import BaseModel


class AvailabilityCreate(BaseModel):
    day_of_week: int
    start_time: time
    end_time: time


class AvailabilityResponse(AvailabilityCreate):
    id: int
    doctor_id: int
    is_active: bool
