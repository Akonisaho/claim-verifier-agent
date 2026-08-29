# Improvement Changelog

Every number below comes from an actual run of `baseline.py`, `app.py`, or
`evaluate.py` against `llama3.2:3b` via Ollama — none of it is hand-written.
Full raw output for the final, reproducible run is in `evidence/results.md`
(with two independent runs, `evidence/results_run1.md` and
`evidence/results_run2.md`, kept as proof of reproducibility).

| Stage | What you tried and why | Evidence | Decision / learning |
|---|---|---|---|
| Baseline | Single prompt: "fact-check this document against this source material," no structure, no context audit. Ollama's default sampling (no fixed temperature/seed). | First real run: 6/10 verdicts matched ground truth. Mismatches were exactly the three deceptive-context cases (2, 6, 7) plus the fabricated-citation edge case (3). | Confirms the thesis before building anything else: a plain fact-checker gets the number right and stops — it has no mechanism to notice the framing is misleading. |
| Iteration 1 | Added atomic claim extraction (split the document claim into standalone facts) + a verify step with an independent `context_audit_flag`, in one pass. Naive extraction prompt (no examples, no format guard). Still default sampling. | First real run: verdict 6/10, audit-flag 5/10, fully-correct 3/10. Real bug found in the raw output: on case_05 (a quote) and case_07 (a percentage claim), the 3B model's extraction step fragmented the statement into meaningless pieces — single words ("satisfied", "with", "the") and tautological non-claims ("The document exists.", "The CEO is a real person."). | Kept the two-step design, but the extraction prompt needed hardening — a small model will literally decompose a sentence word-by-word if not told exactly what "atomic" means and shown examples. |
| Iteration 2 | Hardened the extraction prompt with three worked examples (compound claim, quote, single statistic) and an explicit instruction against generic existence claims. Added a defensive parser guard (`MIN_CLAIM_WORDS`) that discards any extracted "claim" under 3 words as a fragmentation artifact. Still default sampling. | Real run: verdict 7/10, audit-flag 6/10. Case 2 (the key differentiator case) became fully correct: SUPPORTED + `context_audit_flag: True`, matching ground truth exactly. | The prompt fix directly resolved the fragmentation bug and produced the first fully-correct result on the case this project is built around. But a second real run on the same inputs produced *different* verdicts on several cases (case_02 flipped to CONTRADICTED) — a reproducibility problem, not a correctness one. |
| Iteration 3 (final) | Set `temperature: 0` and a fixed `seed` on every Ollama call (both `baseline.py` and `app.py`), since a verification tool whose answer changes between identical runs isn't trustworthy regardless of how accurate any single run looks. | Ran `evaluate.py` twice back-to-back: **byte-for-byte identical results both times** (`evidence/results_run1.md` vs `results_run2.md` — only timestamps differ). Final numbers: baseline 7/10, verifier verdict 7/10, verifier audit-flag 7/10, fully-correct 4/10. | Reproducibility is now real, not assumed. Honest finding: raw verdict accuracy is *tied* with baseline (7/10 each) — the verifier's actual advantage is the `context_audit_flag` dimension, which the baseline has no mechanism for at all. That's the differentiator this project is about, not overall verdict accuracy. |

## The hard case

Case 9 (required): *"Revenue grew 15% and headcount decreased by 10% this
year, showing improved efficiency."* against a source stating revenue grew
15% but headcount *increased* 4%.

Atomic extraction correctly split this into two independent claims —
"Revenue grew 15% this year" (SUPPORTED) and "Headcount decreased by 10%
this year" (CONTRADICTED, since the source says it increased) — and the
roll-up logic correctly took the CONTRADICTED verdict as the document-level
result rather than averaging into a false "mostly true." Verdict: correct,
matching ground truth, in both reproducibility runs.

What it also revealed: the `context_audit_flag` came back `True` on this
case in every real run, when ground truth says `False`. The model's stated
reasoning is that the claim implies a causal link between revenue growth
and headcount reduction ("showing improved efficiency") that the source
doesn't establish — a defensible read of "misleading framing," but not what
the ground truth intends (which is narrowly about the wrong headcount
number, not the efficiency framing). This is a real disagreement about
where the line is between "a false sub-claim" and "a misleadingly framed
true one," and it shows the audit flag is *more* sensitive to inferred
causal framing than the ground truth was designed to test for.

## Failure mode and hot take

The main way this can still go wrong: the two axes (verdict, audit flag)
are decided independently in one model call, and the small model sometimes
conflates them — flagging context-audit on claims that are actually just
compound or inferential, not deceptively-framed (case 9), or missing a
genuine context-manipulation case's core verdict even while nailing another
(case 2 got the flag right but the raw verdict, coincidentally, matches
here since the fact is literally accurate — cases 6 and 7 get the flag
right but the verdict wrong, because the model treats "context was
altered" as evidence the claim itself is unsupported, when the point of an
audit flag is that the claim can be simultaneously accurate *and*
misleading).

The hot take: for an agent whose whole job is "don't just check if the
number matches, check if the framing is honest," reproducibility is not a
nice-to-have — it's a correctness precondition. A verifier that gives a
different verdict each run isn't more or less accurate on any given
question; it means "accuracy" as measured by any single run is close to
meaningless until you've confirmed the pipeline is deterministic. That
should be step one for any agent whose output is meant to be audited by a
human, not an afterthought bolted on once the numbers look good.
