from fastapi import APIRouter
from app.schemas import GenerationRequest
from app.services.generation_service import generate_sentences

router = APIRouter()

@router.post("/generate")
def generate(req: GenerationRequest):
    return generate_sentences(req)