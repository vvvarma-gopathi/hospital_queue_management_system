from datetime import datetime, timedelta
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.appointment import Appointment
from app.repositories.appointment_repository import AppointmentRepository
from app.repositories.doctor_repository import DoctorRepository
from app.repositories.leave_repository import LeaveRepository
from app.repositories.patient_repository import PatientRepository
from app.services.audit_service import AuditService
from app.services.queue_service import QueueService


class AppointmentService:
    def __init__(self):
        self.repo = AppointmentRepository()
        self.patients = PatientRepository()
        self.doctors = DoctorRepository()
        self.leaves = LeaveRepository()

    def create(self, db: Session, data, current_user_id: int):
        patient = self.patients.get(db, data.patient_id)
        doctor = self.doctors.get(db, data.doctor_id)

        if not patient:
            raise HTTPException(404, "Patient not found")
        if not doctor:
            raise HTTPException(404, "Doctor not found")
        if data.duration_minutes <= 0:
            raise HTTPException(400, "Duration must be positive")

        start = data.start_time
        end = (
            datetime.combine(data.appointment_date, start)
            + timedelta(minutes=data.duration_minutes)
        ).time()

        availability = [
            a for a in doctor.availability
            if a.is_active
            and a.day_of_week == data.appointment_date.weekday()
            and a.start_time <= start
            and a.end_time >= end
        ]
        if not availability:
            raise HTTPException(400, "Appointment is outside doctor availability")

        for leave in self.leaves.for_date(db, doctor.id, data.appointment_date):
            leave_start = leave.start_time or start
            leave_end = leave.end_time or end
            if start < leave_end and end > leave_start:
                raise HTTPException(400, "Doctor is on leave for this time")

        overlaps = self.repo.find_overlaps(
            db, doctor.id, data.appointment_date, start, end
        )
        if overlaps:
            raise HTTPException(409, "Doctor already has an appointment in this time")

        appointment = Appointment(
            patient_id=data.patient_id,
            doctor_id=data.doctor_id,
            appointment_date=data.appointment_date,
            start_time=start,
            end_time=end,
            duration_minutes=data.duration_minutes,
            reason=data.reason,
            appointment_type=data.appointment_type,
            created_by=current_user_id,
        )
        result = self.repo.create(db, appointment)
        AuditService.log(
            "APPOINTMENT_BOOKED",
            current_user_id,
            appointment_id=result.id,
            patient_id=result.patient_id,
            doctor_id=result.doctor_id,
        )
        return result

    def get(self, db: Session, appointment_id: int):
        appointment = self.repo.get(db, appointment_id)
        if not appointment:
            raise HTTPException(404, "Appointment not found")
        return appointment

    def list_all(self, db: Session, appointment_date=None):
        return self.repo.list_all(db, appointment_date)

    def doctor_appointments(self, db: Session, doctor_id: int, appointment_date=None):
        return self.repo.list_for_doctor(db, doctor_id, appointment_date)

    def patient_appointments(self, db: Session, patient_id: int):
        return self.repo.list_for_patient(db, patient_id)

    def cancel(self, db: Session, appointment_id: int, user_id: int):
        appointment = self.get(db, appointment_id)

        if appointment.status in {"COMPLETED", "CANCELLED"}:
            raise HTTPException(400, "Appointment cannot be cancelled")

        appointment.status = "CANCELLED"
        db.commit()
        db.refresh(appointment)

        AuditService.log(
            "APPOINTMENT_CANCELLED",
            user_id,
            appointment_id=appointment.id,
        )
        return appointment

    def check_in(self, db: Session, appointment_id: int, user_id: int):
        appointment = self.get(db, appointment_id)

        if appointment.status != "SCHEDULED":
            raise HTTPException(400, "Only scheduled appointments can be checked in")

        appointment.status = "CHECKED_IN"
        AuditService.log("PATIENT_CHECKED_IN", user_id, appointment_id=appointment.id)

        # Checking in is the hand-off from appointments to the live queue.
        # Keep this atomic so a successful check-in always creates the queue entry.
        QueueService().add_appointment_to_queue(db, appointment_id, user_id)
        db.refresh(appointment)
        return appointment
