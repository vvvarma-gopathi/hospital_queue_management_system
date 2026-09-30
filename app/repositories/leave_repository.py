from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.doctor_leave import DoctorLeave


class LeaveRepository:
    def for_date(self, db: Session, doctor_id: int, leave_date):
        return list(
            db.scalars(
                select(DoctorLeave).where(
                    DoctorLeave.doctor_id == doctor_id,
                    DoctorLeave.leave_date == leave_date,
                )
            )
        )

    def create(self, db: Session, leave: DoctorLeave):
        db.add(leave)
        db.commit()
        db.refresh(leave)
        return leave
