import pytest

from doc_review_agent.config import (
    DEFAULT_BASE_URL,
    DEFAULT_MODEL,
    ConfigError,
    load_llm_config,
)


def test_openai_env_takes_precedence_over_aihubmix_and_keyring():
    config = load_llm_config(
        env={
            "OPENAI_API_KEY": "key-openai",
            "AIHUBMIX_API_KEY": "key-aihubmix",
            "OPENAI_BASE_URL": "https://example.com/v1/",
            "OPENAI_MODEL": "test-model",
        },
        keyring_get_password=lambda service, username: "key-keyring",
    )
    assert config.api_key == "key-openai"
    assert config.base_url == "https://example.com/v1"
    assert config.model == "test-model"


def test_aihubmix_env_used_when_openai_unset():
    config = load_llm_config(
        env={"AIHUBMIX_API_KEY": "key-aihubmix", "AIHUBMIX_BASE_URL": "https://hub.example/v1"},
        keyring_get_password=lambda service, username: None,
    )
    assert config.api_key == "key-aihubmix"
    assert config.base_url == "https://hub.example/v1"


def test_keyring_fallback_and_defaults():
    config = load_llm_config(
        env={},
        keyring_get_password=lambda service, username: "key-keyring",
    )
    assert config.api_key == "key-keyring"
    assert config.base_url == DEFAULT_BASE_URL
    assert config.model == DEFAULT_MODEL
    assert config.max_retries == 3
    assert config.max_workers == 4
    assert config.language == "zh"


def test_missing_key_raises_config_error():
    with pytest.raises(ConfigError):
        load_llm_config(env={}, keyring_get_password=lambda service, username: None)


def test_review_settings_read_from_env():
    config = load_llm_config(
        env={
            "OPENAI_API_KEY": "key",
            "OPENAI_MAX_RETRIES": "5",
            "REVIEW_MAX_WORKERS": "8",
            "REVIEW_LANGUAGE": "en",
            "REVIEW_MAX_CHUNK_CHARS": "4000",
        },
        keyring_get_password=lambda service, username: None,
    )
    assert config.max_retries == 5
    assert config.max_workers == 8
    assert config.language == "en"
    assert config.max_chunk_chars == 4000
