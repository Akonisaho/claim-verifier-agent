"""Unit tests for baseline.py — parsing, test-case loading, and retry logic.

No real network/Ollama calls here: these test the pure functions (prompt
parsing, test case loading) and the retry behavior against a mocked
requests.post. Real model output is covered by evaluate.py's
evidence/results.md, generated from an actual run.
"""
from unittest.mock import patch

import pytest
import requests

import baseline


def test_load_test_cases_finds_all_ten():
    cases = baseline.load_test_cases()
    assert len(cases) == 10
    ids = {c["id"] for c in cases}
    assert ids == {f"case_{i:02d}" for i in range(1, 11)}


def test_load_test_cases_have_required_fields():
    for case in baseline.load_test_cases():
        assert "claim" in case
        assert "source" in case
        assert case["ground_truth_verdict"] in baseline.VALID_VERDICTS
        assert isinstance(case["ground_truth_audit_flag"], bool)


def test_parse_response_extracts_verdict_and_reasoning():
    text = "VERDICT: CONTRADICTED\nREASONING: The numbers do not match."
    parsed = baseline.parse_response(text)
    assert parsed.verdict == "CONTRADICTED"
    assert parsed.reasoning == "The numbers do not match."


def test_parse_response_defaults_to_unverifiable_on_garbage():
    parsed = baseline.parse_response("this response has no expected format at all")
    assert parsed.verdict == "UNVERIFIABLE"


def test_build_prompt_includes_claim_and_source():
    prompt = baseline.build_prompt("claim text", "source text")
    assert "claim text" in prompt
    assert "source text" in prompt


class _FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


def test_call_ollama_retries_then_succeeds():
    """A transient failure followed by a good response should still
    return the model's output, not raise."""
    calls = {"n": 0}

    def flaky_post(*args, **kwargs):
        calls["n"] += 1
        if calls["n"] < 2:
            raise requests.ConnectionError("connection refused")
        return _FakeResponse({"response": "VERDICT: SUPPORTED"})

    with patch("baseline.requests.post", side_effect=flaky_post):
        result = baseline.call_ollama("prompt", retries=3)

    assert result == "VERDICT: SUPPORTED"
    assert calls["n"] == 2


def test_call_ollama_raises_after_exhausting_retries():
    """Every attempt failing should raise RuntimeError, not hang or
    silently swallow the error."""
    with (
        patch("baseline.requests.post", side_effect=requests.Timeout("timed out")),
        pytest.raises(RuntimeError, match="failed after 2 attempts"),
    ):
        baseline.call_ollama("prompt", retries=2)
