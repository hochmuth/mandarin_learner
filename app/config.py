import os
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config.toml"


@dataclass(frozen=True)
class GenerationConfig:
    model: str
    max_attempts: int
    reasoning_effort: str | None


@dataclass(frozen=True)
class UIConfig:
    max_selected_characters: int
    default_sentence_count: int
    loading_message_interval_ms: int
    loading_messages: tuple[str, ...]


@dataclass(frozen=True)
class AppConfig:
    generation: GenerationConfig
    ui: UIConfig


def _read_config_file() -> dict[str, Any]:
    config_path = Path(os.getenv("APP_CONFIG_FILE", DEFAULT_CONFIG_PATH))
    if not config_path.exists():
        return {}

    with config_path.open("rb") as config_file:
        return tomllib.load(config_file)


def _get_section(config_data: dict[str, Any], name: str) -> dict[str, Any]:
    section = config_data.get(name, {})
    return section if isinstance(section, dict) else {}


def _load_config() -> AppConfig:
    config_data = _read_config_file()
    generation_data = _get_section(config_data, "generation")
    ui_data = _get_section(config_data, "ui")

    generation = GenerationConfig(
        model=os.getenv("GENERATION_MODEL", generation_data.get("model", "gpt-5")),
        max_attempts=int(
            os.getenv(
                "GENERATION_MAX_ATTEMPTS",
                str(generation_data.get("max_attempts", 3)),
            )
        ),
        reasoning_effort=os.getenv(
            "GENERATION_REASONING_EFFORT",
            generation_data.get("reasoning_effort"),
        ),
    )

    loading_messages = ui_data.get(
        "loading_messages",
        [
            "Just a moment...",
            "Still working...",
            "耐心是一种美德",
            "This is taking forever, isn't it",
        ],
    )
    if not isinstance(loading_messages, list) or not all(
        isinstance(message, str) for message in loading_messages
    ):
        loading_messages = ["Just a moment..."]

    ui = UIConfig(
        max_selected_characters=int(ui_data.get("max_selected_characters", 3)),
        default_sentence_count=int(ui_data.get("default_sentence_count", 3)),
        loading_message_interval_ms=int(ui_data.get("loading_message_interval_ms", 3000)),
        loading_messages=tuple(loading_messages),
    )

    return AppConfig(generation=generation, ui=ui)


settings = _load_config()

GENERATION_MODEL = settings.generation.model
GENERATION_MAX_ATTEMPTS = settings.generation.max_attempts
GENERATION_REASONING_EFFORT = settings.generation.reasoning_effort
UI_MAX_SELECTED_CHARACTERS = settings.ui.max_selected_characters
UI_DEFAULT_SENTENCE_COUNT = settings.ui.default_sentence_count
UI_LOADING_MESSAGE_INTERVAL_MS = settings.ui.loading_message_interval_ms
UI_LOADING_MESSAGES = settings.ui.loading_messages
