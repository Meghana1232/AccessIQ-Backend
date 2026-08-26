from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import LoginHistory
from app.utils.security import get_current_employee


router = APIRouter(
    prefix="/login-history",
    tags=["Login History"]
)


@router.get("/")
def get_login_history(
    db: Session = Depends(get_db),
    employee_id: str = Depends(get_current_employee)
):

    history = (
        db.query(LoginHistory)
        .filter(LoginHistory.employee_id == employee_id)
        .order_by(LoginHistory.login_time.desc())
        .all()
    )

    return {
        "employee_id": employee_id,
        "login_history": history
    }