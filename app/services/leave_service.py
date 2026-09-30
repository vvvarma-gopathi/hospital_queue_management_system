from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.doctor_leave import DoctorLeave
from app.repositories.doctor_repository import DoctorRepository
from app.repositories.leave_repository import LeaveRepository


class LeaveService:
    def __init__(self):
        self.repo = LeaveRepository()
        self.doctors = DoctorRepository()

    def create(self, db: Session, doctor_id: int, data):
        if not self.doctors.get(db, doctor_id):
            raise HTTPException(404, "Doctor not found")

        if data.start_time and data.end_time and data.start_time >= data.end_time:
            raise HTTPException(400, "Start time must be before end time")

        leave = DoctorLeave(doctor_id=doctor_id, **data.model_dump())
        return self.repo.create(db, leave)
