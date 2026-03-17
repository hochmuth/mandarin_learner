from fastapi import FastAPI
from dotenv import load_dotenv
load_dotenv(dotenv_path=".env")

from app.routes.generate import router as generate_router


app = FastAPI(
    title="Mandarin Learning API",
    version="0.1"
)

@app.get("/")
def root():
    return {"status": "API running"}

app.include_router(generate_router)