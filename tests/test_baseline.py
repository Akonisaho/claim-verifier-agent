"""Unit tests for baseline.py — parsing and test-case loading only.

No network/Ollama calls here: these test the pure functions (prompt
parsing, test case loading), not the model itself. Real model output is
covered by evaluate.py's evidence/results.md, generated from an actual run.
"""
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
