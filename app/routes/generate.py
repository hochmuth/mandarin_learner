from fastapi import APIRouter
from app.schemas import GenerationRequest, SentenceResult
from app.services.generation_service import generate_sentences

router = APIRouter()

@router.post("/generate", response_model=list[SentenceResult])
def generate(req: GenerationRequest):

    result = generate_sentences(req)

    return result