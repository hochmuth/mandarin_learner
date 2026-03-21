import json
import os
from app.config import GENERATION_MAX_ATTEMPTS, GENERATION_MODEL
from langfuse import observe
from langfuse.openai import OpenAI
from app.services.validator import validate_sentences

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def build_prompt(
        characters_required: list[str],
        characters_optional: list[str],
        n_sentences: int,
        strict: bool = False,
        invalid_chars=None) -> str:
    char_string_required = " ".join(characters_required)
    char_string_optional = " ".join(characters_optional)

    prompt = f"""
You are helping a beginner learn Mandarin Chinese.

You MUST use characters from this exact list:
{char_string_required}

You can also use any of these additional characters:
{char_string_optional}

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

@observe(name="generate_sentences", as_type="chain")
def generate_sentences(
        characters_required: list[str],
        characters_optional: list[str],
        n_sentences: int):

    last_invalid_chars = []
    last_output = None
    allowed_characters = characters_required + characters_optional

    for attempt in range(GENERATION_MAX_ATTEMPTS):

        strict = attempt > 0

        prompt = build_prompt(
            characters_required,
            characters_optional,
            n_sentences,
            strict=strict,
            invalid_chars=last_invalid_chars
        )

        response = client.responses.create(
            model=GENERATION_MODEL,
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
        valid, invalid_chars = validate_sentences(parsed, allowed_characters)

        if valid:
            return {
                "valid": True,
                "attempts": attempt + 1,
                "sentences": parsed
            }

        last_invalid_chars = list(invalid_chars)

    return {
        "valid": False,
        "attempts": GENERATION_MAX_ATTEMPTS,
        "invalid_characters": last_invalid_chars,
        "raw_output": last_output
    }

def parse_response(text: str):
    try:
        return json.loads(text)
    except Exception:
        return None
