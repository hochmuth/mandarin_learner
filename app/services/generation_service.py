import os
from openai import OpenAI
from app.schemas import GenerationRequest
from app.services.validator import validate_characters_verbose

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def build_prompt(characters: list[str], n_sentences: int) -> str:
    char_string = " ".join(characters)

    return f"""
You are helping a beginner learn Mandarin Chinese.

Use ONLY the following characters:
{char_string}

Rules:
- Do NOT use any characters outside this list
- Write {n_sentences} short sentences
- Keep grammar simple
- Use everyday situations

Return format:

Chinese: <sentence>
Pinyin: <pinyin>
English: <translation>
"""


def generate_sentences(req: GenerationRequest):

    prompt = build_prompt(req.characters, req.n_sentences)

    response = client.responses.create(
        model="gpt-5",
        input=prompt
    )

    text_output = response.output_text

    valid, invalid_chars = validate_characters_verbose(
        text_output,
        req.characters
    )

    return {
        "valid": valid,
        "invalid_characters": list(invalid_chars),
        "raw_output": text_output
    }