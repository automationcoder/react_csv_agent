from contextlib import contextmanager
from typing import Generator

from sqlalchemy.orm import Session

from project.db.database import SessionLocal


@contextmanager
def transaction() -> Generator[Session, None, None]:
    db = SessionLocal()

    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
