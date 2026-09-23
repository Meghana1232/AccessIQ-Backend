from fastapi import APIRouter, Depends, Form
from sqlalchemy.orm import Session

from app.database import get_db

from app.services.alert_service import (
    create_alert,
    get_alerts,
    mark_alert_as_read
)

from app.utils.security import get_current_employee


router = APIRouter(
    prefix="/alerts",
    tags=["Alerts"]
)


@router.post("/")
def add_alert(
    employee_id: str = Form(...),
    title: str = Form(...),
    message: str = Form(...),
    db: Session = Depends(get_db),
    current_employee: str = Depends(get_current_employee)
):
    return create_alert(
        db=db,
        employee_id=employee_id,
        title=title,
        message=message
    )


@router.get("/")
def get_my_alerts(
    db: Session = Depends(get_db),
    employee_id: str = Depends(get_current_employee)
):
    return get_alerts(
        db=db,
        employee_id=employee_id
    )


@router.put("/{alert_id}/read")
def read_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    employee_id: str = Depends(get_current_employee)
):
    return mark_alert_as_read(
        db=db,
        alert_id=alert_id,
        employee_id=employee_id
    )