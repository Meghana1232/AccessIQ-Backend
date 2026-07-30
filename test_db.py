from app.database import SessionLocal
from app.models import User

db = SessionLocal()

try:
    users = db.query(User).all()

    print("\n===== USERS TABLE =====")

    if not users:
        print("No users found.")
    else:
        for user in users:
            print(f"ID: {user.id}")
            print(f"Name: {user.name}")
            print(f"Email: {user.email}")
            print(f"Password: {user.password}")
            print(f"Face Registered: {user.face_registered}")
            print(f"Created At: {user.created_at}")
            print("-" * 40)

finally:
    db.close()