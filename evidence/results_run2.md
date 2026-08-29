# Evaluation results

Generated 2026-08-29T20:46:49.623831+00:00 by running `evaluate.py` against model `llama3.2:3b` via Ollama at `http://localhost:11434`. Every value below is real output from that run — nothing is hand-written.

## Per-case comparison

| Case | Ground truth (verdict / audit) | Baseline verdict | Baseline match | Verifier verdict / audit | Verifier match (verdict / audit) |
|---|---|---|---|---|---|
| case_01: Flipped statistic | CONTRADICTED / False | CONTRADICTED | ✅ | CONTRADICTED / True | ✅ / ❌ |
| case_02: Deceptive context (the key case) | SUPPORTED / True | CONTRADICTED | ❌ | CONTRADICTED / True | ❌ / ✅ |
| case_03: Fabricated citation | UNVERIFIABLE / False | UNVERIFIABLE | ✅ | UNVERIFIABLE / False | ✅ / ✅ |
| case_04: Correct claim, no issues | SUPPORTED / False | SUPPORTED | ✅ | SUPPORTED / False | ✅ / ✅ |
| case_05: Quote misattribution | CONTRADICTED / False | CONTRADICTED | ✅ | CONTRADICTED / True | ✅ / ❌ |
| case_06: Timeline shift | SUPPORTED / True | CONTRADICTED | ❌ | CONTRADICTED / True | ❌ / ✅ |
| case_07: Population/scope shift | SUPPORTED / True | CONTRADICTED | ❌ | CONTRADICTED / True | ❌ / ✅ |
| case_08: Vague, unverifiable forward-looking claim | UNVERIFIABLE / False | UNVERIFIABLE | ✅ | UNVERIFIABLE / False | ✅ / ✅ |
| case_09: Partially correct, partially wrong compound claim (hard case) | CONTRADICTED / False | CONTRADICTED | ✅ | CONTRADICTED / True | ✅ / ❌ |
| case_10: Correct quote, correctly attributed | SUPPORTED / False | SUPPORTED | ✅ | SUPPORTED / False | ✅ / ✅ |

## Summary

- Test cases: 10
- Baseline verdict accuracy: 7/10 (245.5s total)
- Verifier verdict accuracy: 7/10 (1162.5s total)
- Verifier context-audit-flag accuracy: 7/10
- Verifier fully correct (verdict AND audit flag): 4/10

## Key differentiator case (case_02: deceptive context)

- Baseline verdict: CONTRADICTED (baseline has no context-audit mechanism at all)
- Verifier verdict: CONTRADICTED, context_audit_flag: True
- Ground truth: SUPPORTED, context_audit_flag: True
