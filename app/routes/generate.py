from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.schemas import GenerationRequest
from app.database import get_session
from app.services.vocabulary_service import get_characters_by_ids
from app.services.generation_service import generate_sentences

router = APIRouter()

@router.post("/generate")
def generate(
    req: GenerationRequest,
    session: Session = Depends(get_session)
):
    # Step 1: fetch characters from DB
    characters = get_characters_by_ids(session, req.character_ids)

    # Step 2: call generation service
    result = generate_sentences(
        characters=characters,
        n_sentences=req.n_sentences
    )

    return result