# Test cases — known ground truth

Each case: an input document claim + source material + a ground-truth
verdict and expected context_audit_flag. Run baseline and verifier on the
identical cases, then compare each to ground truth.

---

## Case 1 — Flipped statistic
**Input claim**: "Our operational adjustments worked flawlessly, with total
enterprise churn decreasing by 14% year-over-year."
**Source**: "Corporate audit log: total annual churn spiked from 10% up to
24% over the fiscal period."
**Ground truth verdict**: CONTRADICTED
**Ground truth audit flag**: False
**Tests**: Does the system catch a direct factual reversal, not just a
missing fact?

---

## Case 2 — Deceptive context (the key case)
**Input claim**: "Our enterprise threat prevention suite verified a
flawless 99.8% catch rate out of the box during production runs."
**Source**: "SecOps whitepaper: the system achieved a 99.8% catch rate
exclusively inside a static 100-file sandbox environment, but failed live
wild variants."
**Ground truth verdict**: SUPPORTED (the number itself is accurate)
**Ground truth audit flag**: True (the claim omits that this was sandbox-only,
not production, and implies broader reliability than demonstrated)
**Tests**: This is the core differentiator. A baseline comparing numbers
alone will likely just say "supported" and stop there. The verifier should
separately flag that the framing is misleading even though the number matches.

---

## Case 3 — Fabricated citation
**Input claim**: "We remain the dominant provider with a 67% market share
across the continent, according to the Pan-African Tech Registry."
**Source**: "Internal report: the company remains active in multiple
regions. No registry updates or verified market share assessments were
compiled this quarter."
**Ground truth verdict**: UNVERIFIABLE
**Ground truth audit flag**: False
**Tests**: Does the system correctly say "no evidence for this" instead of
guessing it's probably fine, or wrongly calling it contradicted?

---

## Case 4 — Correct claim, no issues
**Input claim**: "Customer support response times improved to under 2
hours on average in Q3."
**Source**: "Support operations report: average first-response time in Q3
was 1 hour 48 minutes, down from 3 hours 10 minutes in Q2."
**Ground truth verdict**: SUPPORTED
**Ground truth audit flag**: False
**Tests**: A clean, easy positive case — the system shouldn't over-flag
things that are genuinely fine.

---

## Case 5 — Quote misattribution
**Input claim**: The document quotes the CFO as saying "we expect
double-digit growth next year."
**Source**: Earnings call transcript shows the CFO actually said "we're
hoping for growth, though it's too early to give a specific number."
**Ground truth verdict**: CONTRADICTED
**Ground truth audit flag**: False
**Tests**: Does the system compare exact quoted language, not just the
general gist?

---

## Case 6 — Timeline shift
**Input claim**: "Revenue grew 20% this quarter."
**Source**: "Revenue grew 20% over the trailing twelve months, not this
quarter specifically — quarterly growth was 3%."
**Ground truth verdict**: SUPPORTED
**Ground truth audit flag**: True (number is real, but the time period was
swapped, which changes the meaning substantially)
**Tests**: A second, distinct example of context manipulation — this time
via timeframe rather than test conditions, to make sure the audit flag
generalizes rather than only catching one specific pattern.

---

## Case 7 — Population/scope shift
**Input claim**: "94% of our customers are satisfied with the product."
**Source**: "94% of customers who responded to our optional survey (12% of
total customers) rated the product positively."
**Ground truth verdict**: SUPPORTED
**Ground truth audit flag**: True (the number is accurate for respondents,
but presented as if it applies to all customers, not just the 12% who
opted to respond)
**Tests**: A third context-manipulation pattern — the scope/population was
narrowed but the claim implies the full population.

---

## Case 8 — Vague, unverifiable forward-looking claim
**Input claim**: "We expect to be the market leader within five years."
**Source**: Any company report with no forward projections included.
**Ground truth verdict**: UNVERIFIABLE
**Ground truth audit flag**: False
**Tests**: Does the system correctly treat a prediction as unverifiable
rather than trying to force a supported/contradicted verdict onto opinion?

---

## Case 9 (hard case) — Partially correct, partially wrong compound claim
**Input claim**: "Revenue grew 15% and headcount decreased by 10% this
year, showing improved efficiency."
**Source**: "Revenue grew 15% this year. Headcount increased by 4% this
year."
**Ground truth verdict**: CONTRADICTED (the headcount part is factually
wrong, even though the revenue part is correct)
**Ground truth audit flag**: False
**Tests**: This is your required "challenging case." A compound claim with
one true and one false part is genuinely tricky — does atomic extraction
correctly split this into two separate claims and verify each on its own,
or does it average into a wrong overall "mostly true" verdict? Write up
what this reveals in your changelog.

---

## Case 10 — Correct quote, correctly attributed
**Input claim**: The document quotes the CEO saying "our top priority
remains customer trust."
**Source**: Press release with that exact quote from the CEO.
**Ground truth verdict**: SUPPORTED
**Ground truth audit flag**: False
**Tests**: Another clean positive control case for quotes specifically.
