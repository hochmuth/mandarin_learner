from pydantic import BaseModel, Field
from app.config import UI_DEFAULT_SENTENCE_COUNT, UI_MAX_SELECTED_CHARACTERS

class GenerationRequest(BaseModel):
    character_ids: list[int] = Field(min_length=1, max_length=UI_MAX_SELECTED_CHARACTERS)
    n_sentences: int = UI_DEFAULT_SENTENCE_COUNT

class SentenceResult(BaseModel):
    chinese: str
    pinyin: str
    english: str

class CharacterCreate(BaseModel):
    character: str
    pinyin: str
    meaning: str
    level: int
    status: str

class CharacterRead(BaseModel):
    id: int
    character: str
    pinyin: str
    meaning: str
    level: int
    status: str
