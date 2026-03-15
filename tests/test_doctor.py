from agx_core.config import Settings
from agx_core.doctor import run_doctor


class FakeAdapter:
    def __init__(self, models, error=None) -> None:
        self.models = models
        self.error = error

    def list_models(self):
        return self.models, self.error


def test_run_doctor_fails_without_api_key() -> None:
    report = run_doctor(
        Settings(
            provider="anthropic",
            base_url="https://api.anthropic.com",
            api_key="",
            timeout_seconds=10,
        ),
        adapter=FakeAdapter([], None),
    )

    assert report.status == "failed"
    assert report.api_key_configured is False


def test_run_doctor_warns_when_alias_targets_are_missing(monkeypatch) -> None:
    monkeypatch.setenv("AGX_MODEL_ALIASES_JSON", '{"sonnet":"claude-sonnet","opus":"claude-opus"}')

    report = run_doctor(
        Settings(
            provider="anthropic",
            base_url="https://api.anthropic.com",
            api_key="dummy",
            timeout_seconds=10,
        ),
        adapter=FakeAdapter(["claude-sonnet"]),
    )

    assert report.status == "warning"
    assert any("Some AGX model aliases are not advertised by the current backend" in note for note in report.notes)


def test_run_doctor_is_healthy_when_models_are_visible() -> None:
    report = run_doctor(
        Settings(
            provider="openai-compatible",
            base_url="https://api.openai.com/v1",
            api_key="dummy",
            timeout_seconds=10,
        ),
        adapter=FakeAdapter(["model-a", "model-b"]),
    )

    assert report.status == "healthy"
    assert report.model_count == 2

