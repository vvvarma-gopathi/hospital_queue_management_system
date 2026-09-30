from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.availability import DoctorAvailability
from app.repositories.availability_repository import AvailabilityRepository
from app.repositories.doctor_repository import DoctorRepository
from app.services.audit_service import AuditService


class AvailabilityService:
    def __init__(self):
        self.repo = AvailabilityRepository()
        self.doctors = DoctorRepository()

    def create(self, db: Session, doctor_id: int, data, user_id=None):
        doctor = self.doctors.get(db, doctor_id)
        if not doctor:
            raise HTTPException(404, "Doctor not found")
        if data.day_of_week not in range(7):
            raise HTTPException(400, "day_of_week must be between 0 and 6")
        if data.start_time >= data.end_time:
            raise HTTPException(400, "Start time must be before end time")

        availability = DoctorAvailability(
            doctor_id=doctor_id,
            **data.model_dump(),
        )
        result = self.repo.create(db, availability)
        AuditService.log(
            "AVAILABILITY_UPDATED",
            user_id,
            doctor_id=doctor_id,
            availability_id=result.id,
        )
        return result

    def list(self, db: Session, doctor_id: int):
        return self.repo.list_for_doctor(db, doctor_id)
