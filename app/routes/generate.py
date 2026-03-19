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
    db_characters = get_characters_by_ids(session, req.character_ids)

    if not db_characters:
        return {"error": "No valid characters found"}

    # Extract just the Chinese characters for generation
    character_list = [c.character for c in db_characters]

    # Step 2: generate sentences
    result = generate_sentences(
        characters=character_list,
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
                "level": c.level
            }
            for c in db_characters
        ]
    }