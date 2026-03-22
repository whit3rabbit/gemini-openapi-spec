# gemini-openapi-spec

Community-maintained OpenAPI specifications for the Google Gemini API. Google does not publish an official OpenAPI spec, so this repo generates one from their public documentation, discovery endpoint, and SDK sources, then compares it against the OpenAI API spec to surface differences.

## Specs

| Spec | Description |
|------|-------------|
| [`gemini-native.openapi.json`](openapi/gemini-native.openapi.json) | Gemini Developer API (v1beta), all documented operations with concrete schemas |
| [`gemini-openai-compat.openapi.json`](openapi/gemini-openai-compat.openapi.json) | Gemini's OpenAI-compatible surface (`/v1beta/openai`), filtered from the upstream OpenAI spec with Gemini extensions |

Both are OpenAPI 3.1 JSON files. Download them directly or point your tooling at the raw GitHub URLs.

## How it works

Google's API surface is spread across four sources that do not fully agree:

1. **Discovery export** -- machine-readable but reports an older `v1beta3` surface
2. **Live API reference** -- the current `v1beta` surface at [ai.google.dev/api/all-methods](https://ai.google.dev/api/all-methods)
3. **Python SDK** -- the [`google-genai`](https://github.com/googleapis/python-genai) package (exposes extra implementation detail)
4. **OpenAI upstream spec** -- the [openai-openapi](https://github.com/openai/openai-openapi) repo

The build pipeline reconciles these into two specs:

```
 Upstream sources        Build                    Validate & compare
 ───────────────        ─────                    ──────────────────
 Discovery export  ─┐
 Live API docs     ─┼─> Native spec             Coverage checks (zero generic ops)
 Python SDK        ─┘                           Drift reports (docs vs discovery vs SDK)

 OpenAI spec       ───> Compat spec             Compat coverage + watchlist
                        (filtered + extensions)  Redocly lint
```

The native spec is built from the live docs, with Google's resource-name bindings expanded into standard OpenAPI path templates. Streaming endpoints use SSE modeling. Guide-documented routes (batch downloads, file uploads) are included when official guides publish concrete paths.

The compat spec starts from the upstream OpenAI spec, filtered to the subset Gemini documents. Gemini-only extensions are attached as `x-gemini-sdk-extra-body-schema` vendor extensions rather than merged into the upstream wire schema.

Weekly CI detects upstream drift and flags when Google changes their API surface.

## Reports

Each build produces validation and drift reports in [`reports/`](reports/):

- **`drift-summary.md`** -- PR-friendly snapshot of docs vs discovery vs SDK drift
- **`compat-watchlist.md`** -- undocumented gaps between Gemini's compat layer and the OpenAI spec
- **`validation-report.json`** -- native coverage details, generic-op count
- **`source-drift-report.json`** -- full drift data

<details>
<summary><strong>Developer guide</strong></summary>

### Requirements

- Python 3.10+
- Node.js 22+ (for Redocly linting)
- Ruby (for YAML parsing of the OpenAI spec)
- Git submodules (`git clone --recursive`)

### Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[test,validate]"
pre-commit install
```

### Full pipeline

```bash
bash scripts/update-all.sh
```

This runs all steps in order: fetch sources, extract SDK surface, build both specs, validate coverage, generate drift reports, lint, and run schema meta-validation.

### Individual steps

```bash
python3 scripts/refresh_sources.py              # fetch upstream discovery + docs (network)
python3 scripts/extract_python_genai_surface.py  # parse SDK AST
python3 scripts/build_openapi.py                # build native spec
python3 scripts/extract_openai_compat_surface.py # extract compat surface from docs
python3 scripts/build_openai_compat.py          # build compat spec
python3 scripts/validate_surface.py             # native coverage + generic-op check
python3 scripts/validate_openai_compat.py       # compat coverage check
python3 scripts/generate_drift_reports.py       # drift + watchlist reports
python3 scripts/lint_openapi.py                 # Redocly lint (native strict, compat advisory)
python3 scripts/validate_schema.py              # JSON Schema meta-validation
```

Steps 2-8 work offline from cached sources in `sources/`. Step 1 requires network access. Steps 9-10 require Node.js and `jsonschema` respectively.

### Tests

```bash
pytest
```

### Repository layout

```
openapi/                              # generated specs (committed, diffed in CI)
scripts/
  _gemini_common.py                   # shared utilities, constants, HTML parsers, loaders
  native_schema_registry.py           # schema definitions for the native spec
  refresh_sources.py                  # fetch and cache upstream sources
  build_openapi.py                    # assemble native spec
  build_openai_compat.py              # assemble compat spec
  extract_python_genai_surface.py     # parse Python SDK for operation surface
  extract_openai_compat_surface.py    # extract compat operations from docs
  validate_surface.py                 # check native coverage vs docs
  validate_openai_compat.py           # check compat coverage
  generate_drift_reports.py           # drift analysis between sources
  lint_openapi.py                     # Redocly linting wrapper
  validate_schema.py                  # JSON Schema meta-validation
  update-all.sh                       # orchestration script
sources/
  discovery/                          # raw Google Discovery export
  docs/                               # cached HTML snapshots + JSON extracts
  openai/                             # upstream OpenAI spec snapshot
reports/                              # generated validation, drift, lint outputs
reference/python-genai/               # SDK submodule (googleapis/python-genai)
tests/                                # pytest unit tests
```

### CI

**`repo-validation.yml`** (push/PR): rebuilds from checked-in sources, validates both specs, asserts zero generic operations, fails if generated files are stale.

**`upstream-drift.yml`** (weekly): refreshes live upstream inputs, reruns assertions, uploads a drift-change bundle on failure.

### Design notes

- All native operations must have concrete schemas. CI fails on any `GenericJsonObject` fallback.
- `openapi/` and `reports/` are committed so diffs are reviewable in PRs. Rebuild before committing if you change any script.
- Pre-commit hooks run both validation scripts and check that generated files are current.
- Compat lint is advisory only because the upstream OpenAI spec snapshot is not Redocly-clean.
- Where verification is weak, a partial schema is preferred over copying stale shapes from the wrong API version.

</details>

## License

[MIT](LICENSE)
