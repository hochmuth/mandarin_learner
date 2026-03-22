from pydantic import BaseModel, Field

class GenerationRequest(BaseModel):
    character_ids: list[int] = Field(min_length=1, max_length=3)
    n_sentences: int = 3

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
