from pydantic import BaseModel

class GenerationRequest(BaseModel):
    character_ids: list[int]
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
