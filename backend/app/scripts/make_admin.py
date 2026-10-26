"""Turns an existing account into admin (or back with --remove).

Usage, inside the backend folder:
    python -m app.scripts.make_admin <apelido>
    python -m app.scripts.make_admin <apelido> --remove
"""
import sys
from sqlalchemy import select
from app.database import SessionLocal
from app.models.user import User


def main():
    args = [arg for arg in sys.argv[1:] if not arg.startswith("--")]
    if len(args) != 1:
        print(__doc__)
        sys.exit(1)

    is_admin = "--remove" not in sys.argv
    with SessionLocal() as db:
        user = db.execute(select(User).where(User.name == args[0])).scalar_one_or_none()
        if not user:
            print(f"Usuário '{args[0]}' não encontrado")
            sys.exit(1)
        user.is_admin = is_admin
        db.commit()
    print(f"{args[0]}: admin = {is_admin}")


if __name__ == "__main__":
    main()
