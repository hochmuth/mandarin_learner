from sqlmodel import Session, select
from app.models import Character


def get_characters_by_ids(session: Session, ids: list[int]) -> list[Character]:
    statement = select(Character).where(Character.id.in_(ids))
    results = session.exec(statement).all()
    return results