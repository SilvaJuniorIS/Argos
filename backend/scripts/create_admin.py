import sys
from pathlib import Path

from sqlalchemy import select

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.core.config import settings  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.db.session import SessionLocal  # noqa: E402
from app.models.user import User, UserRole  # noqa: E402


def create_admin() -> None:
    with SessionLocal() as session:
        admin = session.scalar(select(User).where(User.email == settings.admin_email))
        password_hash = hash_password(settings.admin_password)

        if admin is None:
            admin = User(
                nome="Administrador ARGOS",
                email=settings.admin_email,
                hashed_password=password_hash,
                role=UserRole.admin.value,
                is_active=True,
            )
            session.add(admin)
        else:
            admin.hashed_password = password_hash
            admin.role = UserRole.admin.value
            admin.is_active = True

        session.commit()

    print(f"Admin pronto: {settings.admin_email} / {settings.admin_password}")


if __name__ == "__main__":
    create_admin()
