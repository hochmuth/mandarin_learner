from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.schemas import GenerationRequest
from app.database import get_session
from app.services.vocabulary_service import (
    get_characters_by_ids,
    get_characters_by_status,
)
from app.services.generation_service import generate_sentences

router = APIRouter()


@router.post("/generate")
def generate(
    req: GenerationRequest,
    session: Session = Depends(get_session)
):
    # Step 1: fetch characters from DB
    db_characters = get_characters_by_ids(session, req.character_ids)
    known_characters = get_characters_by_status(session, "known")

    if not db_characters:
        return {"error": "No valid characters found"}

    required_characters = [
        c.character for c in db_characters if c.status == "new"
    ]
    optional_characters = [c.character for c in known_characters]

    if not required_characters:
        return {"error": "No new characters selected"}

    # Step 2: generate sentences
    result = generate_sentences(
        characters_required=required_characters,
        characters_optional=optional_characters,
        n_sentences=req.n_sentences
    )

    # Step 3: attach metadata
    return {
        **result,
        "characters": [
            {
                "id": c.id,
                "character": c.character,
                "pinyin": c.pinyin,
                "meaning": c.meaning,
                "level": c.level,
                "status": c.status,
            }
            for c in db_characters
        ]
    }
