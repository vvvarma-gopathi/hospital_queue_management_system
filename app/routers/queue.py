from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_roles
from app.permissions.roles import ADMIN, DOCTOR, PATIENT, RECEPTIONIST
from app.schemas.queue import QueueEntryResponse, WaitTimeResponse
from app.services.queue_service import QueueService
from app.services.wait_time_service import WaitTimeEstimator

router = APIRouter(prefix="/queue", tags=["Queue"])
service = QueueService()
estimator = WaitTimeEstimator()


@router.post("/appointment/{appointment_id}", response_model=QueueEntryResponse)
def add_to_queue(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN, PATIENT, RECEPTIONIST)),
):
    return service.add_appointment_to_queue(db, appointment_id, current_user.id)


@router.get("/patient/{patient_id}", response_model=list[QueueEntryResponse])
def patient_queue(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN, PATIENT, RECEPTIONIST)),
):
    if current_user.role.name == PATIENT:
        if not current_user.patient or current_user.patient.id != patient_id:
            from fastapi import HTTPException
            raise HTTPException(403, "You can only access your own queue status")
    return service.patient_queue(db, patient_id)


@router.get("/doctor/{doctor_id}", response_model=list[QueueEntryResponse])
def waiting(
    doctor_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(require_roles(ADMIN, DOCTOR, RECEPTIONIST)),
):
    return service.waiting(db, doctor_id)


@router.post("/doctor/{doctor_id}/call-next", response_model=QueueEntryResponse)
def call_next(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN, DOCTOR, RECEPTIONIST)),
):
    return service.call_next(db, doctor_id, current_user.id)


@router.post("/{entry_id}/start", response_model=QueueEntryResponse)
def start(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN, DOCTOR)),
):
    return service.start_consultation(db, entry_id, current_user.id)


@router.post("/{entry_id}/complete", response_model=QueueEntryResponse)
def complete(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN, DOCTOR)),
):
    return service.complete(db, entry_id, current_user.id)


@router.get("/doctor/{doctor_id}/wait-time", response_model=WaitTimeResponse)
def wait_time(
    doctor_id: int,
    queue_number: int,
    db: Session = Depends(get_db),
    _: object = Depends(require_roles(ADMIN, DOCTOR, PATIENT, RECEPTIONIST)),
):
    minutes = estimator.estimate(db, doctor_id, queue_number)
    return {
        "doctor_id": doctor_id,
        "queue_number": queue_number,
        "estimated_wait_minutes": minutes,
    }
