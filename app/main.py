from fastapi import FastAPI
from app.routes.generate import router as generate_router

app = FastAPI(
    title="Mandarin Learning API",
    description="POC backend for constrained Mandarin sentence generation",
    version="0.1"
)

@app.get("/")
def root():
    return {"status": "API running"}

app.include_router(generate_router)