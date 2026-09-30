from datetime import date, datetime, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.queue_entry import QueueEntry
from app.repositories.appointment_repository import AppointmentRepository
from app.repositories.queue_repository import QueueRepository
from app.services.audit_service import AuditService


class QueueService:
    def __init__(self):
        self.repo = QueueRepository()
        self.appointments = AppointmentRepository()

    def add_appointment_to_queue(self, db: Session, appointment_id: int, user_id: int):
        appointment = self.appointments.get(db, appointment_id)
        if not appointment:
            raise HTTPException(404, "Appointment not found")

        if appointment.status != "CHECKED_IN":
            raise HTTPException(400, "Appointment must be checked in before entering the queue")

        if appointment.queue_entry:
            return appointment.queue_entry

        number = self.repo.next_number(db, appointment.doctor_id, date.today())
        entry = QueueEntry(
            appointment_id=appointment.id,
            patient_id=appointment.patient_id,
            doctor_id=appointment.doctor_id,
            queue_number=number,
            status="WAITING",
        )
        appointment.status = "IN_QUEUE"
        result = self.repo.create(db, entry)

        AuditService.log(
            "QUEUE_ENTRY_CREATED",
            user_id,
            queue_entry_id=result.id,
            appointment_id=appointment.id,
        )
        return result

    def waiting(self, db: Session, doctor_id: int):
        return self.repo.waiting(db, doctor_id)

    def patient_queue(self, db: Session, patient_id: int):
        return self.repo.waiting_for_patient(db, patient_id)

    def call_next(self, db: Session, doctor_id: int, user_id: int):
        waiting = self.repo.waiting(db, doctor_id)
        if not waiting:
            raise HTTPException(404, "No waiting patients")

        entry = waiting[0]
        entry.status = "CALLED"
        entry.called_at = datetime.now(timezone.utc).replace(tzinfo=None)

        if entry.appointment:
            entry.appointment.status = "IN_CONSULTATION"

        db.commit()
        db.refresh(entry)

        AuditService.log(
            "PATIENT_CALLED",
            user_id,
            queue_entry_id=entry.id,
            patient_id=entry.patient_id,
        )
        return entry

    def start_consultation(self, db: Session, entry_id: int, user_id: int):
        entry = self.repo.get(db, entry_id)
        if not entry:
            raise HTTPException(404, "Queue entry not found")
        if entry.status != "CALLED":
            raise HTTPException(400, "Only called patients can start consultation")

        entry.status = "IN_CONSULTATION"
        db.commit()
        db.refresh(entry)
        return entry

    def complete(self, db: Session, entry_id: int, user_id: int):
        entry = self.repo.get(db, entry_id)
        if not entry:
            raise HTTPException(404, "Queue entry not found")
        if entry.status != "IN_CONSULTATION":
            raise HTTPException(400, "Patient is not in consultation")

        entry.status = "COMPLETED"
        entry.completed_at = datetime.now(timezone.utc).replace(tzinfo=None)
        if entry.appointment:
            entry.appointment.status = "COMPLETED"

        db.commit()
        db.refresh(entry)

        AuditService.log(
            "QUEUE_COMPLETED",
            user_id,
            queue_entry_id=entry.id,
            patient_id=entry.patient_id,
        )
        return entry
