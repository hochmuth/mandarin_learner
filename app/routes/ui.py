from fastapi import APIRouter, Depends, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
from sqlmodel import Session, select

from app.database import get_session
from app.models import Character
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
    character_ids: list[int] = Form(...),
    n_sentences: int = Form(2),
    session: Session = Depends(get_session)
):
    characters = session.exec(
        select(Character).where(Character.id.in_(character_ids))
    ).all()

    char_list = [c.character for c in characters]

    result = generate_sentences(
        characters=char_list,
        n_sentences=n_sentences
    )

    # Render result HTML
    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "result": result,
            "characters": characters
        }
    )
