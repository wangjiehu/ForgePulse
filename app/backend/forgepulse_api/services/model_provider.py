from __future__ import annotations

import json
import os
from typing import Protocol
from urllib import error, request

from pydantic import BaseModel, Field, ValidationError

from forgepulse_api.schemas import AgentReasoning, CandidateNote, Diagnosis


class NarrativeEnhancement(BaseModel):
    mode: str
    summary: str
    referenced_evidence_ids: list[str] = Field(default_factory=list)
    warning: str | None = None


class ModelProvider(Protocol):
    name: str

    def enhance(self, diagnosis: Diagnosis) -> NarrativeEnhancement:
        """Enhance wording without changing deterministic diagnosis facts."""

    def reason(self, diagnosis: Diagnosis) -> AgentReasoning | None:
        """Produce an advisory LLM review of the deterministic diagnosis.

        Returns None when no LLM is configured (offline mode). The returned
        review never overrides structured diagnosis fields; it only contributes
        natural-language review, uncertainty flags, and safety reaffirmation.
        """


class OfflineModelProvider:
    name = "offline"

    def enhance(self, diagnosis: Diagnosis) -> NarrativeEnhancement:
        return NarrativeEnhancement(
            mode=self.name,
            summary=diagnosis.incident_summary,
            referenced_evidence_ids=[],
            warning="Model enhancement is disabled; deterministic output is unchanged.",
        )

    def reason(self, diagnosis: Diagnosis) -> AgentReasoning | None:
        return None



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

    def reason(self, diagnosis: Diagnosis) -> AgentReasoning | None:
        """Call the LLM to produce an advisory review of the deterministic diagnosis.

        The structured diagnosis is never modified. The model's response is
        validated against the evidence-id and candidate-id whitelists; on any
        validation or transport failure the method returns an AgentReasoning
        with ``warning`` set and empty review fields (deterministic output
        unchanged).
        """
        allowed_evidence_ids = sorted(item.id for item in diagnosis.evidence)
        candidate_ids = sorted(
            item.candidate_id
            for item in (
                list(diagnosis.root_cause_candidates)
                + list(diagnosis.contributing_factors)
                + list(diagnosis.downstream_effects)
            )
        )
        primary = diagnosis.primary_root_cause
        payload = {
            "model": self.model,
            "response_format": {"type": "json_object"},
            "temperature": 0,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are ForgePulse, an industrial maintenance diagnosis review agent. "
                        "Review the diagnosis a deterministic evidence engine produced. "
                        "You are advisory: do NOT change diagnosis status, root-cause candidates, "
                        "confidence, scores, or actions. Only refine rationale wording, flag "
                        "uncertainties, and reaffirm safety. "
                        "Only use evidence ids from allowed_evidence_ids and candidate_id values "
                        "from root_cause_candidates. Return JSON with keys: review_summary, "
                        "candidate_notes (list of {candidate_id, rationale_refined, why_ranked_refined}), "
                        "uncertainties (list[str]), safety_reaffirmation (str), "
                        "referenced_evidence_ids (list[str])."
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "diagnosis_status": diagnosis.diagnosis_status,
                            "incident_summary": diagnosis.incident_summary,
                            "primary_root_cause": (
                                {
                                    "candidate_id": primary.candidate_id,
                                    "title": primary.title,
                                    "confidence": primary.confidence,
                                    "rationale": primary.rationale,
                                }
                                if primary
                                else None
                            ),
                            "root_cause_candidates": [
                                {
                                    "candidate_id": item.candidate_id,
                                    "title": item.title,
                                    "confidence": item.confidence,
                                    "rationale": item.rationale,
                                    "why_ranked": item.why_ranked,
                                }
                                for item in diagnosis.root_cause_candidates
                            ],
                            "missing_evidence": diagnosis.missing_evidence,
                            "conflicting_evidence": diagnosis.conflicting_evidence,
                            "recommended_actions": [
                                {"action_id": a.action_id, "title": a.title}
                                for a in diagnosis.recommended_actions
                            ],
                            "allowed_evidence_ids": allowed_evidence_ids,
                            "allowed_candidate_ids": candidate_ids,
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
        except (
            error.URLError,
            TimeoutError,
            OSError,
            UnicodeError,
            TypeError,
            KeyError,
            IndexError,
            json.JSONDecodeError,
        ) as exc:
            return AgentReasoning(
                mode=self.name,
                review_summary="",
                warning=f"LLM review failed; deterministic diagnosis retained: {exc}",
            )

        try:
            notes: list[CandidateNote] = []
            for note in parsed.get("candidate_notes", []) or []:
                cid = note.get("candidate_id", "")
                if cid and cid in candidate_ids:
                    notes.append(CandidateNote(
                        candidate_id=cid,
                        rationale_refined=note.get("rationale_refined", "") or "",
                        why_ranked_refined=note.get("why_ranked_refined", "") or "",
                    ))
            referenced = [i for i in (parsed.get("referenced_evidence_ids", []) or []) if i in set(allowed_evidence_ids)]
            reasoning = AgentReasoning(
                mode=self.name,
                review_summary=(parsed.get("review_summary", "") or "").strip(),
                candidate_notes=notes,
                uncertainties=[str(u) for u in (parsed.get("uncertainties", []) or []) if str(u).strip()],
                safety_reaffirmation=(parsed.get("safety_reaffirmation", "") or "").strip(),
                referenced_evidence_ids=sorted(set(referenced)),
            )
        except (ValidationError, AttributeError, TypeError) as exc:
            return AgentReasoning(
                mode=self.name,
                review_summary="",
                warning=f"LLM review output invalid; deterministic diagnosis retained: {exc}",
            )

        # If the model referenced forbidden evidence ids, retain valid ones but warn.
        raw_ids = parsed.get("referenced_evidence_ids", []) or []
        forbidden = sorted(set(raw_ids) - set(allowed_evidence_ids))
        if forbidden:
            reasoning.warning = (
                "Model referenced unknown evidence ids; those were dropped: "
                + ", ".join(forbidden)
            )
        return reasoning



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
