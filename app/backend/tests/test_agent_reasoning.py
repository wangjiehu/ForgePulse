"""Tests for the advisory LLM reasoning layer (agent_reasoning)."""

from __future__ import annotations

import json

from forgepulse_api.schemas import AgentReasoning, CandidateNote
from forgepulse_api.services.diagnosis import build_diagnosis
from forgepulse_api.services.model_provider import OpenAICompatibleModelProvider


CASE_ID = "coating_line_dryer_tension_001"


def _install_fake_provider(monkeypatch, review_factory):
    """Replace get_model_provider in both the model_provider and diagnosis modules."""
    from forgepulse_api.services import diagnosis as diagnosis_module
    from forgepulse_api.services import model_provider as mp_module

    class FakeProvider:
        name = "openai_compatible"

        def enhance(self, diagnosis):
            return None

        def reason(self, diagnosis):
            return review_factory(diagnosis)

    monkeypatch.setattr(mp_module, "get_model_provider", lambda: FakeProvider())
    monkeypatch.setattr(diagnosis_module, "get_model_provider", mp_module.get_model_provider)


def test_offline_mode_has_no_agent_reasoning():
    diagnosis = build_diagnosis(CASE_ID)
    assert diagnosis.agent_reasoning is None
    assert any("no LLM reasoning applied" in line for line in diagnosis.limitations)
    assert not any(d.state == "llm_review" for d in diagnosis.agent_decisions)


def test_llm_review_attached_when_provider_configured(monkeypatch):
    def review_factory(diagnosis):
        cid = diagnosis.primary_root_cause.candidate_id
        return AgentReasoning(
            mode="openai_compatible",
            review_summary="Evidence supports the primary candidate.",
            candidate_notes=[CandidateNote(candidate_id=cid, rationale_refined="refined")],
            uncertainties=["Confirm fan inspection record."],
            safety_reaffirmation="Confirm with engineer before repair.",
            referenced_evidence_ids=[diagnosis.evidence[0].id],
        )

    _install_fake_provider(monkeypatch, review_factory)
    diagnosis = build_diagnosis(CASE_ID, reasoning="auto")

    assert diagnosis.agent_reasoning is not None
    assert diagnosis.agent_reasoning.mode == "openai_compatible"
    assert diagnosis.agent_reasoning.review_summary
    assert any(d.state == "llm_review" for d in diagnosis.agent_decisions)
    assert any("advisory" in line for line in diagnosis.limitations)
    assert not any("no LLM reasoning applied" in line for line in diagnosis.limitations)


def test_reasoning_off_skips_llm_even_with_provider(monkeypatch):
    def review_factory(diagnosis):
        return AgentReasoning(mode="openai_compatible", review_summary="should not appear")

    _install_fake_provider(monkeypatch, review_factory)
    diagnosis = build_diagnosis(CASE_ID, reasoning="off")

    assert diagnosis.agent_reasoning is None
    assert not any(d.state == "llm_review" for d in diagnosis.agent_decisions)
    assert any("no LLM reasoning applied" in line for line in diagnosis.limitations)


def test_llm_review_does_not_change_structured_diagnosis(monkeypatch):
    def review_factory(diagnosis):
        return AgentReasoning(
            mode="openai_compatible",
            review_summary="review",
            candidate_notes=[
                CandidateNote(candidate_id=diagnosis.primary_root_cause.candidate_id)
            ],
            referenced_evidence_ids=[diagnosis.evidence[0].id],
        )

    _install_fake_provider(monkeypatch, review_factory)

    offline = build_diagnosis(CASE_ID)
    reviewed = build_diagnosis(CASE_ID, reasoning="auto")

    assert reviewed.diagnosis_status == offline.diagnosis_status
    assert reviewed.primary_root_cause.confidence == offline.primary_root_cause.confidence
    assert reviewed.primary_root_cause.candidate_id == offline.primary_root_cause.candidate_id
    assert [c.candidate_id for c in reviewed.root_cause_candidates] == [
        c.candidate_id for c in offline.root_cause_candidates
    ]
    assert [a.action_id for a in reviewed.recommended_actions] == [
        a.action_id for a in offline.recommended_actions
    ]


def test_offline_determinism_preserved():
    first = build_diagnosis(CASE_ID).model_dump()
    second = build_diagnosis(CASE_ID).model_dump()
    assert first == second


def test_reasoning_unknown_evidence_ids_are_dropped(monkeypatch):
    def review_factory(diagnosis):
        return AgentReasoning(
            mode="openai_compatible",
            review_summary="review",
            referenced_evidence_ids=["EV-DOES-NOT-EXIST"],
        )

    _install_fake_provider(monkeypatch, review_factory)
    diagnosis = build_diagnosis(CASE_ID, reasoning="auto")

    assert diagnosis.agent_reasoning is not None
    assert diagnosis.agent_reasoning.referenced_evidence_ids == []


def test_openai_provider_reason_transport_failure_returns_warning(monkeypatch):
    diagnosis = build_diagnosis(CASE_ID)
    monkeypatch.setattr(
        "forgepulse_api.services.model_provider.request.urlopen",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(TimeoutError("timed out")),
    )
    provider = OpenAICompatibleModelProvider("http://example.test/v1", "test", "test")
    review = provider.reason(diagnosis)

    assert review is not None
    assert review.review_summary == ""
    assert review.warning and "failed" in review.warning.lower()


def test_openai_provider_reason_parses_valid_response(monkeypatch):
    diagnosis = build_diagnosis(CASE_ID)
    cid = diagnosis.primary_root_cause.candidate_id
    eid = diagnosis.evidence[0].id

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def read(self):
            content = json.dumps({
                "review_summary": "Looks consistent.",
                "candidate_notes": [
                    {"candidate_id": cid, "rationale_refined": "ok", "why_ranked_refined": "ok"}
                ],
                "uncertainties": ["gap"],
                "safety_reaffirmation": "Confirm with engineer.",
                "referenced_evidence_ids": [eid],
            })
            return json.dumps({"choices": [{"message": {"content": content}}]}).encode("utf-8")

    monkeypatch.setattr(
        "forgepulse_api.services.model_provider.request.urlopen",
        lambda *_args, **_kwargs: FakeResponse(),
    )
    provider = OpenAICompatibleModelProvider("http://example.test/v1", "test", "test")
    review = provider.reason(diagnosis)

    assert review.review_summary == "Looks consistent."
    assert review.candidate_notes[0].candidate_id == cid
    assert review.referenced_evidence_ids == [eid]
    assert review.safety_reaffirmation == "Confirm with engineer."
    assert review.warning is None


def test_openai_provider_reason_drops_unknown_candidate_notes(monkeypatch):
    diagnosis = build_diagnosis(CASE_ID)

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def read(self):
            content = json.dumps({
                "review_summary": "review",
                "candidate_notes": [
                    {"candidate_id": "RC-FAKE", "rationale_refined": "x"}
                ],
                "referenced_evidence_ids": [],
            })
            return json.dumps({"choices": [{"message": {"content": content}}]}).encode("utf-8")

    monkeypatch.setattr(
        "forgepulse_api.services.model_provider.request.urlopen",
        lambda *_args, **_kwargs: FakeResponse(),
    )
    provider = OpenAICompatibleModelProvider("http://example.test/v1", "test", "test")
    review = provider.reason(diagnosis)

    assert review.candidate_notes == []
