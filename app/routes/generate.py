from fastapi import APIRouter
from app.schemas import GenerationRequest, SentenceResult
from app.services.generation_service import generate_sentences

router = APIRouter()

@router.post("/generate", response_model=dict)
def generate(req: GenerationRequest):
    return generate_sentences(req)