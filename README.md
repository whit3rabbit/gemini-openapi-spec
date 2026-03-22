# gemini-openapi-spec

OpenAPI workbench for the Gemini Developer API and its OpenAI-compatible surface.

## Upstream sources

This repo reconciles four upstream sources that do not currently agree:

1. **Discovery export** -- `https://generativelanguage.googleapis.com/$discovery/OPENAPI3_0` (reports `v1beta3`, smaller surface)
2. **Live API reference** -- `https://ai.google.dev/api/all-methods` (current `v1beta` surface)
3. **Python SDK** -- [`reference/python-genai`](reference/python-genai) submodule (targets `v1beta`, exposes extra implementation detail)
4. **OpenAI upstream spec** -- `https://raw.githubusercontent.com/openai/openai-openapi/manual_spec/openapi.yaml`

Because of those mismatches, the repo keeps separate native and compatibility tracks.

## Repository layout

```
openapi/
  gemini-native.openapi.json      # generated native v1beta spec
  gemini-openai-compat.openapi.json  # generated OpenAI-compat spec (/v1beta/openai)
scripts/                           # build, validate, lint, drift helpers
sources/
  discovery/                       # raw upstream discovery export
  docs/                            # cached doc extracts (files, batch, models, tokens, etc.)
  openai/                          # upstream OpenAI spec snapshot
reports/                           # generated validation, drift, lint, watchlist outputs
reference/python-genai/            # SDK submodule
```

## Quick start

Run the full pipeline (fetch, build, validate, lint, drift reports):

```bash
bash scripts/update-all.sh
```

Or run individual steps in order:

```bash
python3 scripts/refresh_sources.py          # fetch upstream discovery + docs
python3 scripts/extract_python_genai_surface.py  # extract SDK surface
python3 scripts/build_openapi.py            # build native spec
python3 scripts/extract_openai_compat_surface.py # extract compat surface
python3 scripts/build_openai_compat.py      # build compat spec
python3 scripts/validate_surface.py         # native coverage + generic-op check
python3 scripts/validate_openai_compat.py   # compat coverage check
python3 scripts/generate_drift_reports.py   # drift + watchlist reports
python3 scripts/lint_openapi.py             # Redocly lint (native strict, compat advisory)
```

## Design decisions

### Native spec

- Path and method coverage follows the live `all-methods` docs. Guide-documented extras (e.g., batch download routes) are included when official guides publish concrete routes outside `all-methods`.
- Path templates expand Google resource-name bindings into concrete collection segments (e.g., `/{name=cachedContents/*}` becomes `/cachedContents/{cachedContent}`) to avoid ambiguous OpenAPI paths.
- `streamGenerateContent` is modeled as SSE (`text/event-stream` + `alt=sse`) with an `x-gemini-stream-event-schema` hint, not as a fake JSON response body.
- All native operations have concrete schemas. Zero operations fall back to `GenericJsonObject`.

### Compatibility spec

- Starts from the upstream OpenAI spec, filtered to the subset Google documents.
- Preserves upstream OpenAI request/response schemas where possible.
- Gemini-only extensions are attached as `x-gemini-sdk-extra-body-schema` vendor extensions on operations, not merged into the upstream wire schema.
- Extensions use `extra_body.google.*` (matching Google's JS/REST examples). The Python SDK docs show a double-nested `extra_body` key which appears to be a docs bug and is not encoded.
- Compat lint is advisory only because the upstream OpenAI spec snapshot is not Redocly-clean.

### Schema policy

Where verification is weak, a partial schema is better than copying stale shapes from the wrong version. Request/response schemas stay as generic placeholders unless backed by a verified machine-readable source.

## Validation

| Command | Purpose |
|---------|---------|
| `validate_surface.py` | Native coverage vs docs, fails on any `GenericJsonObject` fallback |
| `validate_openai_compat.py` | Compat coverage, generic-op count, classified upstream-only path summary, compat watchlist |
| `generate_drift_reports.py` | Docs vs discovery drift, SDK vs native drift, compat vs upstream summary |
| `lint_openapi.py` | Redocly lint (native: blocking, compat: advisory) |

Key report files:
- `reports/validation-report.json` -- separates undocumented ops, guide-documented aliases, and reference-documented aliases
- `reports/source-drift-report.json` -- aggregated drift data
- `reports/drift-summary.md` / `drift-summary.json` -- PR-friendly snapshot
- `reports/compat-watchlist.md` -- undocumented compat gaps worth rechecking

## CI

**`repo-validation.yml`** (push/PR): rebuilds from checked-in sources, runs validation + native lint, asserts zero generic operations in both specs, fails if generated files are stale. Uploads drift summary and watchlist as artifacts.

**`upstream-drift.yml`** (weekly schedule): refreshes live upstream inputs, reruns assertions, fails if repo differs from checked-in state. On failure, uploads a drift-change bundle (git status, diff, patch, summaries). Weekly cadence balances signal vs noise.

## Current promoted native schemas

`batches` list/get/delete/cancel, updateGenerateContentBatch/updateEmbedContentBatch |
`fileSearchStores` create/get/list/delete/import/upload, documents list/get/delete |
`models` list/get/countTokens/countMessageTokens/countTextTokens/embedText/batchEmbedText/batchEmbedContents/generateMessage/generateText/predict/predictLongRunning/streamGenerateContent/batchGenerateContent/asyncBatchEmbedContent/generateContent/embedContent |
`cachedContents` create/get/list/patch/delete |
`files` upload/get/list/delete/register
