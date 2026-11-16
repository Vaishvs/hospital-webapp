import getpass

from database import SessionLocal
from database import UserDB
from auth import get_password_hash


def create_admin():

    db = SessionLocal()

    try:
        existing_admin = db.query(UserDB).filter(
            UserDB.role == "admin"
        ).first()

        if existing_admin:
            print("Admin already exists!")
            return

        username = input("Enter Admin username: ")
        email = input("Enter Admin email: ")

        password = getpass.getpass("Enter Admin password: ")
        confirm_password = getpass.getpass("Confirm password: ")

        if password != confirm_password:
            print("Passwords do not match!")
            return

        if len(password) < 12:
            print("Password must be at least 12 characters!")
            return

        admin = UserDB(
            username=username,
            email=email,
            hashed_password=get_password_hash(password),
            role="admin",
            is_active=True
        )

        db.add(admin)
        db.commit()

        print("Admin created successfully!")

    except Exception as e:
        db.rollback()
        print("Error creating admin:", e)

    finally:
        db.close()


if __name__ == "__main__":
    create_admin()

# Your create_admin.py is a standalone utility.
# We want the following behaviour:
# - When you explicitly run python create_admin.py, create the Admin.
# - When another Python file imports create_admin.py, don't create an Admin automatically.
# That's exactly what the main guard achieves.
