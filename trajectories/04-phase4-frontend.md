# Trajectory: Phase 4 — web UI, a real module-collision bug

## Instruction given
"For Phase 4, build the simple Flask page as planned, but also add file
upload support: accept `.txt`, `.pdf`, and `.docx` files for both the
document and source inputs, using pdfplumber for PDF and python-docx for
Word, extracting plain text before passing it to the existing
`app.py`/`baseline.py` functions — no changes to those functions
themselves. Add basic drag-and-drop styling to the upload area. If this
takes more than an hour to get working cleanly, stop and tell me rather
than letting it eat into remaining time."

## Action taken
Built `web/app.py` (a Flask app) that imports `baseline`'s and `app`'s
existing functions directly (`build_prompt`/`call_ollama`/`parse_response`,
and `extract_claims`/`verify_claim`/`rollup`) rather than duplicating any
verification logic, plus templates and a drag-and-drop dropzone.

## Tool response: a real bug, not a hypothetical one
Wrote a smoke test that imported the new web module and called its
`/verify` route against a real Ollama request. It threw:

```
AttributeError: module 'app' has no attribute 'extract_claims'
```

## What it revealed / changed next
Traced this to a genuine Python import collision: the new file was named
`web/app.py`, and the test harness had put `web/` on `sys.path` and
imported it as module `app` *before* `web/app.py`'s own `sys.path.insert`
+ `import app` line ran - so `import app` inside `web/app.py` resolved to
itself (already cached in `sys.modules` under that name) instead of the
real verifier module at the repo root. This is exactly the kind of hidden
dependency-ordering bug that only shows up under a specific import order,
not a hypothetical concern. Fixed it the direct way - renamed the file to
`web/server.py`, eliminating the name collision rather than working around
the import order - and re-ran the same smoke test against a real Ollama
call to confirm the fix, then also verified the file-upload path
end-to-end (a real in-memory `.txt` upload through `/verify`, not just the
pasted-text path).

## Timebox honored
Finished (code, both smoke tests passing against a real Ollama call,
dependency security re-scan clean) within the requested one-hour budget -
did not need to invoke the "stop and tell me" fallback.
