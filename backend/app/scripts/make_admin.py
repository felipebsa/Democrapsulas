"""Turns an existing account into admin.

Usage, inside the backend folder:
    python -m app.scripts.make_admin <apelido>
"""
import sys
from sqlalchemy import select
from app.database import SessionLocal
from app.models.user import User


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)

    name = sys.argv[1]
    with SessionLocal() as db:
        user = db.execute(select(User).where(User.name == name)).scalar_one_or_none()
        if not user:
            print(f"Usuário '{name}' não encontrado")
            sys.exit(1)
        user.is_admin = True
        db.commit()
    print(f"{name} agora é admin")


if __name__ == "__main__":
    main()
