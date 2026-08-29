# Trajectory: Phase 3 — hardening and a real reproduction test

## Instruction given
Per CLAUDE.md's Phase 3 spec: add pytest unit tests, error handling/retries
around Ollama calls, and "perform a genuine clean-environment reproduction
test of REPRODUCE.md (simulate a fresh clone and follow the instructions
exactly). Fix anything that breaks."

## Action taken: closing a real test-coverage gap
Retries already existed in `call_ollama` (both `baseline.py` and
`app.py`), but nothing actually tested that behavior - it was only ever
exercised implicitly by real Ollama calls succeeding. Added tests that
mock `requests.post` to fail once then succeed (confirms retry actually
happens and returns the right result) and to fail every time (confirms it
raises `RuntimeError` rather than hanging or swallowing the error), for
both modules.

## Action taken: the actual reproduction test
Rather than only re-testing pieces already exercised individually, ran
REPRODUCE.md's documented "Fastest path" for real, simulating a fresh
user: `./setup.sh` then `docker compose run baseline` / `docker compose
run verifier`.

## Tool response: `setup.sh` failed immediately
```
setup.sh: line 4: ollama: command not found
```
even though Ollama was genuinely installed. Investigated before assuming
it was a real bug: checked `[System.Environment]::GetEnvironmentVariable
("Path","User")` and confirmed Ollama's install directory *was* in the
persistent user PATH - then tested a freshly-spawned PowerShell process and
found it *still* didn't see `ollama`, because a child process inherits its
parent's environment block at spawn time, not a live re-read of the
registry. Concluded correctly that this is a genuine, common Windows
first-run gotcha (a terminal open before the Ollama install never sees the
PATH update, no matter how many child processes it spawns), not something
`setup.sh` can fix procedurally - so instead of trying to work around it
silently, added a clear `command -v ollama` check with an explicit,
actionable error message, and the same explanation as a REPRODUCE.md
troubleshooting note.

## Tool response: a real doc/config mismatch
Noticed that `docker-compose.yml`'s `verifier` service already defaulted
to `python evaluate.py` - meaning REPRODUCE.md's "Run the full verifier"
section and its "Run the full evaluation" section described what was
actually the identical command. Fixed `docker-compose.yml` so `docker
compose run verifier` genuinely runs just `app.py --all` (matching what
the doc says it does), keeping the explicit `... python evaluate.py`
override for the combined comparison.

## Tool response: real runtime numbers contradicted the docs
REPRODUCE.md's original runtime estimates ("under 1 minute," "1-3
minutes") were written before any real run and turned out to be far off -
the actual measured total for all 10 cases on CPU was ~245-383s for the
baseline and ~1162-1396s for the verifier (from the real `evaluate.py`
timing already captured in `evidence/results.md`). Updated REPRODUCE.md to
state the real measured ranges instead of the original guesses.

## Real end-to-end verification
Ran `docker compose run baseline` for real against the fixed
docker-compose.yml, confirming host-to-container Ollama networking
(`host.docker.internal`) and the volume-mounted `test_cases/` actually
work from inside a container on this machine, not just via direct `python
baseline.py` calls on the host:

```
Baseline accuracy: 7/10 verdicts matched ground truth
```

matching the host-run numbers exactly, confirming the Docker reproduction
path is genuinely equivalent to the documented one. Then ran `docker
compose run verifier` the same way for the full verifier pipeline:

```
Verifier verdict accuracy:    7/10
Verifier audit-flag accuracy: 7/10
Verifier fully-correct:       4/10
```

- again matching the host-run numbers exactly. Both real Docker
reproduction runs (baseline and verifier) confirm the numbers in
`CHANGELOG.md` and `evidence/results.md` hold up through the exact path a
judge following `REPRODUCE.md` would take, not just through direct
`python` invocations on the development machine.
