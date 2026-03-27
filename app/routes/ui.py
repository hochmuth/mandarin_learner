from fastapi import APIRouter, Depends, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
from sqlmodel import Session, select

from app.config import (
    UI_DEFAULT_SENTENCE_COUNT,
    UI_LOADING_MESSAGE_INTERVAL_MS,
    UI_LOADING_MESSAGES,
    UI_MAX_SELECTED_CHARACTERS,
)
from app.database import get_session
from app.models import Character
from app.services.vocabulary_service import get_characters_by_status
from app.services.generation_service import generate_sentences

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def index(request: Request, session: Session = Depends(get_session)):
    characters = session.exec(select(Character)).all()
    new_characters = [char for char in characters if char.status == "new"]

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "new_characters": new_characters,
            "max_selected_characters": UI_MAX_SELECTED_CHARACTERS,
            "default_sentence_count": UI_DEFAULT_SENTENCE_COUNT,
            "loading_messages": list(UI_LOADING_MESSAGES),
            "loading_message_interval_ms": UI_LOADING_MESSAGE_INTERVAL_MS,
        }
    )


@router.get("/known-characters", response_class=HTMLResponse)
def known_characters_page(request: Request, session: Session = Depends(get_session)):
    characters = session.exec(select(Character)).all()
    known_characters = [char for char in characters if char.status == "known"]

    return templates.TemplateResponse(
        "known_characters.html",
        {
            "request": request,
            "known_characters": known_characters,
        }
    )


@router.post("/generate-ui", response_class=HTMLResponse)
def generate_ui(
    request: Request,
    character_ids: list[int] | None = Form(None),
    n_sentences: int = Form(UI_DEFAULT_SENTENCE_COUNT),
    session: Session = Depends(get_session)
):
    if not character_ids:
        return templates.TemplateResponse(
            "result.html",
            {
                "request": request,
                "result": {"valid": False, "attempts": 0},
                "characters": [],
                "error_message": "Select at least one new character.",
            }
        )

    if len(character_ids) > UI_MAX_SELECTED_CHARACTERS:
        return templates.TemplateResponse(
            "result.html",
            {
                "request": request,
                "result": {"valid": False, "attempts": 0},
                "characters": [],
                "error_message": f"Select at most {UI_MAX_SELECTED_CHARACTERS} new characters.",
            }
        )

    selected_new_characters = session.exec(
        select(Character).where(Character.id.in_(character_ids))
    ).all()
    known_characters = get_characters_by_status(session, "known")

    required_characters = [
        c.character for c in selected_new_characters if c.status == "new"
    ]
    optional_characters = [c.character for c in known_characters]

    if not required_characters:
        return templates.TemplateResponse(
            "result.html",
            {
                "request": request,
                "result": {"valid": False, "attempts": 0},
                "characters": selected_new_characters,
                "error_message": "Select at least one new character.",
            }
        )

    result = generate_sentences(
        characters_required=required_characters,
        characters_optional=optional_characters,
        n_sentences=n_sentences
    )

    # Render result HTML
    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "result": result,
            "characters": selected_new_characters
        }
    )
