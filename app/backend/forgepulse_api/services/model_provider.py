from __future__ import annotations

import json
import os
from typing import Protocol
from urllib import error, request

from pydantic import BaseModel, Field, ValidationError

from forgepulse_api.schemas import Diagnosis


class NarrativeEnhancement(BaseModel):
    mode: str
    summary: str
    referenced_evidence_ids: list[str] = Field(default_factory=list)
    warning: str | None = None


class ModelProvider(Protocol):
    name: str

    def enhance(self, diagnosis: Diagnosis) -> NarrativeEnhancement:
        """Enhance wording without changing deterministic diagnosis facts."""


class OfflineModelProvider:
    name = "offline"

    def enhance(self, diagnosis: Diagnosis) -> NarrativeEnhancement:
        return NarrativeEnhancement(
            mode=self.name,
            summary=diagnosis.incident_summary,
            referenced_evidence_ids=[],
            warning="Model enhancement is disabled; deterministic output is unchanged.",
        )


class OpenAICompatibleModelProvider:
    """Optional JSON-only narrative provider for a local or managed compatible gateway."""

    name = "openai_compatible"

    def __init__(self, base_url: str, api_key: str, model: str, timeout_seconds: int = 30):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.timeout_seconds = timeout_seconds

    def enhance(self, diagnosis: Diagnosis) -> NarrativeEnhancement:
        allowed_evidence_ids = sorted(item.id for item in diagnosis.evidence)
        payload = {
            "model": self.model,
            "response_format": {"type": "json_object"},
            "temperature": 0,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You improve the clarity of an industrial diagnosis summary. "
                        "Do not change diagnosis status, root causes, actions, confidence, or safety boundaries. "
                        "Return JSON with summary and referenced_evidence_ids. "
                        "Only use evidence IDs provided by the user."
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "diagnosis_status": diagnosis.diagnosis_status,
                            "incident_summary": diagnosis.incident_summary,
                            "primary_root_cause": (
                                diagnosis.primary_root_cause.model_dump()
                                if diagnosis.primary_root_cause
                                else None
                            ),
                            "missing_evidence": diagnosis.missing_evidence,
                            "conflicting_evidence": diagnosis.conflicting_evidence,
                            "allowed_evidence_ids": allowed_evidence_ids,
                        },
                        ensure_ascii=False,
                    ),
                },
            ],
        }
        http_request = request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with request.urlopen(http_request, timeout=self.timeout_seconds) as response:
                response_payload = json.loads(response.read().decode("utf-8"))
            content = response_payload["choices"][0]["message"]["content"]
            parsed = json.loads(content)
            enhancement = NarrativeEnhancement(
                mode=self.name,
                summary=parsed["summary"],
                referenced_evidence_ids=parsed.get("referenced_evidence_ids", []),
            )
        except (
            error.URLError,
            TimeoutError,
            OSError,
            UnicodeError,
            TypeError,
            KeyError,
            IndexError,
            json.JSONDecodeError,
            ValidationError,
        ) as exc:
            return NarrativeEnhancement(
                mode=self.name,
                summary=diagnosis.incident_summary,
                warning=f"Model enhancement failed; deterministic summary retained: {exc}",
            )

        invalid_ids = sorted(set(enhancement.referenced_evidence_ids) - set(allowed_evidence_ids))
        if invalid_ids:
            return NarrativeEnhancement(
                mode=self.name,
                summary=diagnosis.incident_summary,
                warning=(
                    "Model returned unknown evidence IDs; deterministic summary retained: "
                    + ", ".join(invalid_ids)
                ),
            )
        return enhancement


def get_model_provider() -> ModelProvider:
    provider = os.getenv("FORGEPULSE_MODEL_PROVIDER", "offline").strip().lower()
    if provider == "offline":
        return OfflineModelProvider()
    if provider == "openai_compatible":
        base_url = os.getenv("FORGEPULSE_MODEL_BASE_URL", "").strip()
        api_key = os.getenv("FORGEPULSE_MODEL_API_KEY", "").strip()
        model = os.getenv("FORGEPULSE_MODEL_NAME", "").strip()
        if not base_url or not api_key or not model:
            return OfflineModelProvider()
        return OpenAICompatibleModelProvider(base_url, api_key, model)
    return OfflineModelProvider()
