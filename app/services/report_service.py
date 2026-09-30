from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.appointment import Appointment
from app.models.doctor import Doctor


class ReportService:
    def doctor_workload(self, db: Session):
        doctors = db.query(Doctor).order_by(Doctor.id).all()
        result = []

        for doctor in doctors:
            appointments = (
                db.query(Appointment)
                .filter(Appointment.doctor_id == doctor.id)
                .all()
            )
            result.append({
                "doctor_id": doctor.id,
                "doctor_name": f"{doctor.first_name} {doctor.last_name}",
                "total_appointments": len(appointments),
                "completed_appointments": sum(
                    a.status == "COMPLETED" for a in appointments
                ),
                "cancelled_appointments": sum(
                    a.status == "CANCELLED" for a in appointments
                ),
            })

        return result
