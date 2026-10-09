from fastapi import APIRouter, Depends, Form
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas import (
    AdminUserOut,
    RoleUpdateResponse,
    DeleteUserResponse,
    AdminStatsResponse,
    BroadcastAlertResponse
)
from app.services.admin_service import (
    get_all_users,
    get_user,
    update_user_role,
    delete_user,
    get_admin_stats,
    broadcast_alert
)
from app.utils.security import get_current_admin


router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


@router.get("/users", response_model=List[AdminUserOut])
def list_users(
    db: Session = Depends(get_db),
    admin_id: str = Depends(get_current_admin)
):
    return get_all_users(db)


@router.get("/users/{employee_id}", response_model=AdminUserOut)
def view_user(
    employee_id: str,
    db: Session = Depends(get_db),
    admin_id: str = Depends(get_current_admin)
):
    return get_user(db, employee_id)


@router.put("/users/{employee_id}/role", response_model=RoleUpdateResponse)
def change_user_role(
    employee_id: str,
    role: str = Form(..., description="'employee' or 'admin'"),
    db: Session = Depends(get_db),
    admin_id: str = Depends(get_current_admin)
):
    return update_user_role(db, employee_id, role)


@router.delete(
    "/users/{employee_id}",
    response_model=DeleteUserResponse,
    summary="Delete an employee (irreversible)",
    description="Permanently deletes an employee, their login history, "
                "inbox messages, alerts, and stored face image."
)
def remove_user(
    employee_id: str,
    db: Session = Depends(get_db),
    admin_id: str = Depends(get_current_admin)
):
    return delete_user(db, employee_id)


@router.get(
    "/stats",
    response_model=AdminStatsResponse,
    summary="Dashboard summary stats"
)
def dashboard_stats(
    db: Session = Depends(get_db),
    admin_id: str = Depends(get_current_admin)
):
    return get_admin_stats(db)


@router.post(
    "/alerts/broadcast",
    response_model=BroadcastAlertResponse,
    summary="Send an alert to every employee"
)
def broadcast(
    title: str = Form(...),
    message: str = Form(...),
    db: Session = Depends(get_db),
    admin_id: str = Depends(get_current_admin)
):
    return broadcast_alert(db, title, message)