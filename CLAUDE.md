# CLAUDE.md

OpenAPI workbench for the Gemini Developer API. Generates and validates native and OpenAI-compatible specs by reconciling upstream sources (Discovery export, live docs, Python SDK, OpenAI spec).

## Project layout

- `scripts/` -- all build, extract, validate, and lint scripts
- `scripts/_gemini_common.py` -- shared utilities, constants, HTML parsers, loaders
- `scripts/native_schema_registry.py` -- schema definitions for the native spec
- `openapi/` -- generated specs (committed, diffed in CI)
- `sources/` -- cached upstream sources (HTML snapshots, JSON extracts, discovery export)
- `reports/` -- generated validation and drift reports (committed, diffed in CI)
- `reference/python-genai/` -- git submodule (googleapis/python-genai)
- `tests/` -- pytest unit tests

## Build pipeline

Full pipeline: `bash scripts/update-all.sh`

Individual steps in order:
1. `refresh_sources.py` -- fetch upstream sources (hits network)
2. `extract_python_genai_surface.py` -- parse SDK AST
3. `build_openapi.py` -- assemble native spec
4. `extract_openai_compat_surface.py` -- extract compat surface from docs
5. `build_openai_compat.py` -- assemble compat spec
6. `validate_surface.py` -- check native coverage, reject generics
7. `validate_openai_compat.py` -- check compat coverage
8. `generate_drift_reports.py` -- source drift analysis
9. `lint_openapi.py` -- Redocly linting (requires Node 22+)
10. `validate_schema.py` -- JSON Schema meta-validation (requires `jsonschema`)

Steps 2-8 work offline from cached sources. Step 1 requires network. Steps 9-10 require external tools.

## Running tests

```
pip install -e ".[test]"
pytest
```

## Key constraints

- Python 3.10+, no production dependencies (stdlib only for scripts).
- `openapi/` and `reports/` are committed and CI asserts `git diff --exit-code` on them. Rebuild before committing if you change any script.
- Zero generic operations allowed: CI fails if any `GenericJsonObject` fallbacks remain in either spec.
- Pre-commit hooks run `validate_surface.py`, `validate_openai_compat.py`, and check generated files are current.
- `build_openai_compat.py` uses `load_yaml_via_ruby()` to parse the upstream OpenAI YAML spec (requires Ruby).
