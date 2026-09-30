from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_roles
from app.permissions.roles import ADMIN, DOCTOR, PATIENT, RECEPTIONIST
from app.schemas.availability import AvailabilityCreate, AvailabilityResponse
from app.services.availability_service import AvailabilityService

router = APIRouter(prefix="/availability", tags=["Availability"])
service = AvailabilityService()


@router.post("/doctor/{doctor_id}", response_model=AvailabilityResponse)
def create_availability(
    doctor_id: int,
    data: AvailabilityCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN, DOCTOR)),
):
    if current_user.role.name == DOCTOR:
        if not current_user.doctor or current_user.doctor.id != doctor_id:
            from fastapi import HTTPException
            raise HTTPException(403, "You can only manage your own availability")

    return service.create(db, doctor_id, data, current_user.id)


@router.get("/doctor/{doctor_id}", response_model=list[AvailabilityResponse])
def get_availability(
    doctor_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(require_roles(ADMIN, DOCTOR, PATIENT, RECEPTIONIST)),
):
    return service.list(db, doctor_id)
