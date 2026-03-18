import json
import os
from openai import OpenAI
from app.schemas import GenerationRequest
from app.services.validator import validate_sentences

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def build_prompt(characters: list[str], n_sentences: int, strict: bool = False, invalid_chars=None) -> str:
    char_string = " ".join(characters)

    prompt = f"""
You are helping a beginner learn Mandarin Chinese.

You MUST ONLY use characters from this exact list:
{char_string}

Rules:
- Do NOT use any other Chinese characters
- Write {n_sentences} short sentences
- Keep grammar simple

Output format:
Return ONLY valid JSON (no explanation, no extra text)

Example format:
[
  {{
    "chinese": "我喝水。",
    "pinyin": "wǒ hē shuǐ",
    "english": "I drink water."
  }}
]
"""

    if strict:
        prompt += "\nSTRICT MODE:\n"
        prompt += "- Your previous answer was INVALID.\n"
        if invalid_chars:
            prompt += f"- Forbidden characters used: {' '.join(invalid_chars)}\n"
        prompt += "- You MUST fix all errors.\n"

    return prompt

def generate_sentences(req: GenerationRequest):

    max_attempts = 3
    last_invalid_chars = []
    last_output = None

    for attempt in range(max_attempts):

        strict = attempt > 0

        prompt = build_prompt(
            req.characters,
            req.n_sentences,
            strict=strict,
            invalid_chars=last_invalid_chars
        )

        response = client.responses.create(
            model="gpt-5",
            input=prompt
        )

        text_output = response.output_text
        last_output = text_output

        # Step 1: Parse JSON
        parsed = parse_response(text_output)

        if parsed is None:
            last_invalid_chars = ["INVALID_JSON"]
            continue

        # Step 2: Validate characters
        valid, invalid_chars = validate_sentences(parsed, req.characters)

        if valid:
            return {
                "valid": True,
                "attempts": attempt + 1,
                "sentences": parsed
            }

        last_invalid_chars = list(invalid_chars)

    return {
        "valid": False,
        "attempts": max_attempts,
        "invalid_characters": last_invalid_chars,
        "raw_output": last_output
    }

def parse_response(text: str):
    try:
        return json.loads(text)
    except Exception:
        return None