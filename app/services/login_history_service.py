from sqlalchemy.orm import Session

from app.models import LoginHistory


def create_login_history(
    db: Session,
    employee_id: str,
    login_status: str,
    login_method: str = "Face Recognition"
):

    login_record = LoginHistory(
        employee_id=employee_id,
        login_status=login_status,
        login_method=login_method
    )

    db.add(login_record)
    db.commit()
    db.refresh(login_record)

    return login_record


def get_login_history(db: Session):
    return (
        db.query(LoginHistory)
        .order_by(LoginHistory.login_time.desc())
        .all()
    )