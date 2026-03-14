from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.jwt_handler import get_current_user
from app.models.user import User
from app.schemas.report import ProjectReport
from app.services.report_service import generate_project_report

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/{project_id}", response_model=ProjectReport)
def get_project_report(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return generate_project_report(db, project_id)
