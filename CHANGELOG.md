# Improvement Changelog

Fill in [brackets] with real numbers from actual runs of evaluate.py.
Never write a number here that wasn't produced by actually running the code.

| Stage | What you tried and why | Evidence | Decision / learning |
|---|---|---|---|
| Baseline | Single prompt: "fact-check this document against this source material," no structure. | [accuracy across test_cases — how many verdicts matched ground truth?] | Established the starting point. |
| Iteration 1 | Added atomic claim extraction: decompose the document into individual claims before verifying, instead of judging the whole document at once. | [new accuracy] | [kept / revised / removed — did decomposition alone help, or only once combined with the next step?] |
| Iteration 2 (Final) | Added the independent context_audit_flag: forces the verdict to separately check whether the surrounding context was altered even when the number itself is correct. | [final accuracy, plus specifically: did it catch the "deceptive context" test case that Iteration 1 missed?] | [identify the single change that contributed most] |

## The hard case
[Describe the one test case you deliberately made ambiguous/tricky — what
did the system output, and what did that reveal about its limits?]

## Failure mode and hot take
[What's the main way this can still go wrong? What did building this teach
you about making agents more reliable in general?]
