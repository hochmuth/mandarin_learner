from sqlmodel import SQLModel, Field


class Character(SQLModel, table=True):
    __tablename__ = "characters"

    id: int | None = Field(default=None, primary_key=True)
    character: str
    pinyin: str
    meaning: str
    level: int
    status: str
