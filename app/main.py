from dotenv import load_dotenv
# We need to load .env before the rest of the imports
load_dotenv(dotenv_path=".env")

from fastapi import FastAPI
from app.database import create_db
from app.routes.ui import router as ui_router
from app.routes.generate import router as generate_router
from app.routes.characters import router as characters_router


app = FastAPI(
    title="Mandarin Learning API",
    version="0.1"
)

create_db()

# @app.get("/")
# def root():
#     return {"status": "API running"}

app.include_router(generate_router)
app.include_router(characters_router)
app.include_router(ui_router)