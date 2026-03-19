from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.database import get_session
from app.models import Character
from app.schemas import CharacterCreate, CharacterRead

router = APIRouter(prefix="/characters", tags=["characters"])


@router.post("/", response_model=CharacterRead)
def create_character(
    character: CharacterCreate,
    session: Session = Depends(get_session)
):
    db_char = Character(**character.model_dump())
    session.add(db_char)
    session.commit()
    session.refresh(db_char)
    return db_char


@router.get("/", response_model=list[CharacterRead])
def get_characters(session: Session = Depends(get_session)):
    statement = select(Character)
    results = session.exec(statement).all()
    return results