from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Mapping


class ConfigError(RuntimeError):
    """Raised when required runtime configuration is missing."""


DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_KEYRING_SERVICE = "doc-review-agent"
DEFAULT_KEYRING_USERNAME = "api-key"


@dataclass(frozen=True)
class LLMConfig:
    api_key: str
    base_url: str
    model: str
    temperature: float = 0.1
    timeout_seconds: float = 120.0
    max_chunk_chars: int = 8000
    max_retries: int = 3
    max_workers: int = 4
    language: str = "zh"


def load_dotenv_file(path: str | Path = ".env") -> None:
    env_path = Path(path)
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def load_llm_config(
    env: Mapping[str, str] | None = None,
    keyring_get_password: Callable[[str, str], str | None] | None = None,
) -> LLMConfig:
    source = env if env is not None else os.environ
    keyring_service = source.get("AIHUBMIX_KEYRING_SERVICE", DEFAULT_KEYRING_SERVICE).strip()
    keyring_username = source.get("AIHUBMIX_KEYRING_USERNAME", DEFAULT_KEYRING_USERNAME).strip()
    api_key = (
        source.get("OPENAI_API_KEY", "").strip()
        or source.get("AIHUBMIX_API_KEY", "").strip()
        or _load_keyring_password(
            service=keyring_service,
            username=keyring_username,
            getter=keyring_get_password,
        )
    )

    if not api_key:
        raise ConfigError(
            "Missing API key. Set OPENAI_API_KEY or AIHUBMIX_API_KEY (see .env.example), "
            f"or store it in keyring with service '{keyring_service}' "
            f"and username '{keyring_username}' via the store-key command."
        )

    return LLMConfig(
        api_key=api_key,
        base_url=(
            source.get("OPENAI_BASE_URL", "").strip()
            or source.get("AIHUBMIX_BASE_URL", "").strip()
            or DEFAULT_BASE_URL
        ).rstrip("/"),
        model=(
            source.get("OPENAI_MODEL", "").strip()
            or source.get("AIHUBMIX_MODEL", "").strip()
            or DEFAULT_MODEL
        ),
        temperature=float(source.get("OPENAI_TEMPERATURE", "0.1")),
        timeout_seconds=float(source.get("OPENAI_TIMEOUT_SECONDS", "120")),
        max_chunk_chars=int(source.get("REVIEW_MAX_CHUNK_CHARS", "8000")),
        max_retries=int(source.get("OPENAI_MAX_RETRIES", "3")),
        max_workers=int(source.get("REVIEW_MAX_WORKERS", "4")),
        language=source.get("REVIEW_LANGUAGE", "zh").strip() or "zh",
    )


def _load_keyring_password(
    *,
    service: str,
    username: str,
    getter: Callable[[str, str], str | None] | None,
) -> str:
    keyring_get_password = getter or _default_keyring_get_password
    value = keyring_get_password(service, username)
    return (value or "").strip()


def _default_keyring_get_password(service: str, username: str) -> str | None:
    try:
        import keyring
    except ImportError:
        return None

    try:
        return keyring.get_password(service, username)
    except Exception:  # noqa: BLE001 - no usable keyring backend (headless/CI); fall through to ConfigError
        return None
