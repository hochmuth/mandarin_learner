from fastapi import APIRouter, Depends, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
from sqlmodel import Session, select

from app.database import get_session
from app.models import Character
from app.services.vocabulary_service import get_characters_by_status
from app.services.generation_service import generate_sentences

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def index(request: Request, session: Session = Depends(get_session)):
    characters = session.exec(select(Character)).all()
    known_characters = [char for char in characters if char.status == "known"]
    new_characters = [char for char in characters if char.status == "new"]

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "known_characters": known_characters,
            "new_characters": new_characters,
        }
    )


@router.post("/generate-ui", response_class=HTMLResponse)
def generate_ui(
    request: Request,
    character_ids: list[int] | None = Form(None),
    n_sentences: int = Form(2),
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
