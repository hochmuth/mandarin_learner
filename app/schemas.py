from pydantic import BaseModel

class GenerationRequest(BaseModel):
    characters: list[str]
    n_sentences: int = 3


class SentenceResult(BaseModel):
    chinese: str
    pinyin: str
    english: str