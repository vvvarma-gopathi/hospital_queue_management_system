from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_roles
from app.permissions.roles import ADMIN, DOCTOR
from app.schemas.doctor_leave import LeaveCreate, LeaveResponse
from app.services.leave_service import LeaveService

router = APIRouter(prefix="/leaves", tags=["Doctor Leave"])
service = LeaveService()


@router.post("/doctor/{doctor_id}", response_model=LeaveResponse)
def create_leave(
    doctor_id: int,
    data: LeaveCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN, DOCTOR)),
):
    if current_user.role.name == DOCTOR:
        if not current_user.doctor or current_user.doctor.id != doctor_id:
            from fastapi import HTTPException
            raise HTTPException(403, "You can only manage your own leave")

    return service.create(db, doctor_id, data)
