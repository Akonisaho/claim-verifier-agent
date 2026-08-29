"""Unit tests for app.py — parsing, extraction fallback, and roll-up logic.

No network/Ollama calls: these test the pure functions. Real model output
is covered by evaluate.py's evidence/results.md, generated from an actual run.
"""
import app


def test_parse_claims_splits_multiple_claim_lines():
    text = "CLAIM: revenue grew 15%\nCLAIM: headcount decreased 10%"
    claims = app.parse_claims(text, fallback="unused")
    assert [c.text for c in claims] == ["revenue grew 15%", "headcount decreased 10%"]


def test_parse_claims_falls_back_to_original_on_empty_output():
    claims = app.parse_claims("no CLAIM lines here", fallback="original statement")
    assert [c.text for c in claims] == ["original statement"]


def test_parse_verdict_extracts_all_fields():
    text = (
        "VERDICT: SUPPORTED\n"
        "CONTEXT_AUDIT: YES\n"
        "SOURCE_QUOTE: 99.8% catch rate in a sandbox\n"
        "REASONING: number matches but conditions differ."
    )
    verdict = app.parse_verdict(text, claim="claim text")
    assert verdict.verdict == "SUPPORTED"
    assert verdict.context_audit_flag is True
    assert verdict.source_quote == "99.8% catch rate in a sandbox"
    assert verdict.reasoning == "number matches but conditions differ."


def test_parse_verdict_audit_flag_no():
    text = "VERDICT: SUPPORTED\nCONTEXT_AUDIT: NO\nSOURCE_QUOTE: x\nREASONING: fine."
    verdict = app.parse_verdict(text, claim="claim text")
    assert verdict.context_audit_flag is False


def test_rollup_any_contradicted_wins():
    claims = [
        app.ClaimVerdict(claim="a", verdict="SUPPORTED", context_audit_flag=False,
                          source_quote="", reasoning=""),
        app.ClaimVerdict(claim="b", verdict="CONTRADICTED", context_audit_flag=False,
                          source_quote="", reasoning=""),
    ]
    verdict, audit_flag = app.rollup(claims)
    assert verdict == "CONTRADICTED"
    assert audit_flag is False


def test_rollup_unverifiable_beats_supported():
    claims = [
        app.ClaimVerdict(claim="a", verdict="SUPPORTED", context_audit_flag=False,
                          source_quote="", reasoning=""),
        app.ClaimVerdict(claim="b", verdict="UNVERIFIABLE", context_audit_flag=False,
                          source_quote="", reasoning=""),
    ]
    verdict, _audit_flag = app.rollup(claims)
    assert verdict == "UNVERIFIABLE"


def test_rollup_audit_flag_true_if_any_claim_flagged():
    claims = [
        app.ClaimVerdict(claim="a", verdict="SUPPORTED", context_audit_flag=True,
                          source_quote="", reasoning=""),
        app.ClaimVerdict(claim="b", verdict="SUPPORTED", context_audit_flag=False,
                          source_quote="", reasoning=""),
    ]
    verdict, audit_flag = app.rollup(claims)
    assert verdict == "SUPPORTED"
    assert audit_flag is True


def test_load_test_cases_finds_all_ten():
    cases = app.load_test_cases()
    assert len(cases) == 10
