from __future__ import annotations

import json

from forgepulse_api.services.diagnosis import build_diagnosis
from forgepulse_api.services.model_provider import (
    OfflineModelProvider,
    OpenAICompatibleModelProvider,
    get_model_provider,
)


def test_default_model_provider_is_offline(monkeypatch):
    monkeypatch.delenv("FORGEPULSE_MODEL_PROVIDER", raising=False)
    assert isinstance(get_model_provider(), OfflineModelProvider)


def test_incomplete_model_configuration_falls_back_offline(monkeypatch):
    monkeypatch.setenv("FORGEPULSE_MODEL_PROVIDER", "openai_compatible")
    monkeypatch.delenv("FORGEPULSE_MODEL_API_KEY", raising=False)
    monkeypatch.delenv("FORGEPULSE_MODEL_BASE_URL", raising=False)
    monkeypatch.delenv("FORGEPULSE_MODEL_NAME", raising=False)
    assert isinstance(get_model_provider(), OfflineModelProvider)


def test_offline_provider_keeps_deterministic_summary():
    diagnosis = build_diagnosis("coating_line_dryer_tension_001")
    result = OfflineModelProvider().enhance(diagnosis)
    assert result.mode == "offline"
    assert result.summary == diagnosis.incident_summary


def test_provider_rejects_unknown_evidence_ids(monkeypatch):
    diagnosis = build_diagnosis("coating_line_dryer_tension_001")

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def read(self):
            content = json.dumps({
                "summary": "Enhanced summary",
                "referenced_evidence_ids": ["EV-999"],
            })
            return json.dumps({
                "choices": [{"message": {"content": content}}],
            }).encode("utf-8")

    monkeypatch.setattr(
        "forgepulse_api.services.model_provider.request.urlopen",
        lambda *_args, **_kwargs: FakeResponse(),
    )
    provider = OpenAICompatibleModelProvider("http://example.test/v1", "test", "test")
    result = provider.enhance(diagnosis)
    assert result.summary == diagnosis.incident_summary
    assert "unknown evidence IDs" in (result.warning or "")


def test_provider_falls_back_on_timeout(monkeypatch):
    diagnosis = build_diagnosis("coating_line_dryer_tension_001")
    monkeypatch.setattr(
        "forgepulse_api.services.model_provider.request.urlopen",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(TimeoutError("timed out")),
    )

    provider = OpenAICompatibleModelProvider("http://example.test/v1", "test", "test")
    result = provider.enhance(diagnosis)

    assert result.summary == diagnosis.incident_summary
    assert "failed" in (result.warning or "").lower()
