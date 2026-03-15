from agx_core.config import current_fallbacks, current_model_aliases, fallback_chain, load_settings


def test_load_settings_defaults_to_anthropic(monkeypatch) -> None:
    monkeypatch.delenv("AGX_PROVIDER", raising=False)
    monkeypatch.delenv("AGX_BASE_URL", raising=False)

    settings = load_settings()

    assert settings.provider == "anthropic"
    assert settings.base_url == "https://api.anthropic.com"


def test_current_model_aliases_accepts_json_override(monkeypatch) -> None:
    monkeypatch.setenv("AGX_MODEL_ALIASES_JSON", '{"sonnet":"claude-sonnet","opus":"claude-opus"}')

    aliases = current_model_aliases()

    assert aliases["sonnet"] == "claude-sonnet"
    assert aliases["opus"] == "claude-opus"


def test_current_fallbacks_accepts_json_override(monkeypatch) -> None:
    monkeypatch.setenv("AGX_DEFAULT_FALLBACKS_JSON", '{"sonnet":["opus"],"fast":["strong"]}')

    fallbacks = current_fallbacks()

    assert fallbacks["sonnet"] == ["opus"]
    assert fallbacks["fast"] == ["strong"]


def test_fallback_chain_preserves_primary_first() -> None:
    assert fallback_chain("sonnet", ["opus", "sonnet"]) == ["sonnet", "opus"]

