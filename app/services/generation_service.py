import json
import os
from functools import lru_cache
from pathlib import Path

from app.config import (
    GENERATION_MAX_ATTEMPTS,
    GENERATION_MODEL,
    GENERATION_REASONING_EFFORT,
)
from openai import OpenAI

from app.services.validator import validate_sentences

PROMPTS_DIR = Path(__file__).resolve().parents[1] / "prompts"
GENERATION_PROMPT_PATH = PROMPTS_DIR / "generation_prompt.txt"


def _build_reasoning_kwargs() -> dict:
    if not GENERATION_REASONING_EFFORT:
        return {}

    return {"reasoning": {"effort": GENERATION_REASONING_EFFORT}}

def _noop_observe(*args, **kwargs):
    def decorator(func):
        return func

    return decorator


def _langfuse_base_url() -> str | None:
    return os.getenv("LANGFUSE_HOST") or os.getenv("LANGFUSE_BASE_URL")


def _langfuse_is_configured() -> bool:
    return all(
        (
            os.getenv("LANGFUSE_PUBLIC_KEY"),
            os.getenv("LANGFUSE_SECRET_KEY"),
            _langfuse_base_url(),
        )
    )


@lru_cache(maxsize=1)
def _get_generation_runtime():
    if _langfuse_is_configured():
        try:
            if not os.getenv("LANGFUSE_HOST"):
                base_url = _langfuse_base_url()
                if base_url:
                    os.environ["LANGFUSE_HOST"] = base_url

            from langfuse import observe
            from langfuse.openai import OpenAI as LangfuseOpenAI

            return LangfuseOpenAI(api_key=os.getenv("OPENAI_API_KEY")), observe
        except Exception:
            pass

    return OpenAI(api_key=os.getenv("OPENAI_API_KEY")), _noop_observe


@lru_cache(maxsize=1)
def _load_generation_prompt_template() -> str:
    return GENERATION_PROMPT_PATH.read_text(encoding="utf-8")


def build_prompt(
        characters_required: list[str],
        characters_optional: list[str],
        n_sentences: int,
        strict: bool = False,
        invalid_chars=None) -> str:
    char_string_required = " ".join(characters_required)
    char_string_optional = " ".join(characters_optional)
    prompt = _load_generation_prompt_template().format(
        char_string_required=char_string_required,
        char_string_optional=char_string_optional,
        n_sentences=n_sentences,
    )

    if strict:
        prompt += "\nSTRICT MODE:\n"
        prompt += "- Your previous answer was INVALID.\n"
        if invalid_chars:
            prompt += f"- Forbidden characters used: {' '.join(invalid_chars)}\n"
        prompt += "- You MUST fix all errors.\n"

    return prompt

def generate_sentences(
        characters_required: list[str],
        characters_optional: list[str],
        n_sentences: int,
        **response_kwargs):
    client, observe = _get_generation_runtime()

    @observe(name="generate_sentences", as_type="chain")
    def _run_generation(
            characters_required: list[str],
            characters_optional: list[str],
            n_sentences: int,
            **response_kwargs):
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
                input=prompt,
                **_build_reasoning_kwargs(),
                **response_kwargs
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

    return _run_generation(
        characters_required=characters_required,
        characters_optional=characters_optional,
        n_sentences=n_sentences,
        **response_kwargs
    )


def parse_response(text: str):
    try:
        return json.loads(text)
    except Exception:
        return None
