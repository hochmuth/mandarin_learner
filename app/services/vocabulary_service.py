from sqlmodel import Session, select
from app.models import Character


def get_characters_by_ids(session: Session, ids: list[int]) -> list[str]:
    statement = select(Character).where(Character.id.in_(ids))
    results = session.exec(statement).all()

    return [char.character for char in results]