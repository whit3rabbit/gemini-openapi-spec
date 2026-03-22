#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

CURRENT_STEP="(init)"
trap 'echo "FAILED at step: $CURRENT_STEP" >&2' ERR

CURRENT_STEP="refresh_sources"
python3 scripts/refresh_sources.py

CURRENT_STEP="extract_python_genai_surface"
python3 scripts/extract_python_genai_surface.py

CURRENT_STEP="build_openapi"
python3 scripts/build_openapi.py

CURRENT_STEP="extract_openai_compat_surface"
python3 scripts/extract_openai_compat_surface.py

CURRENT_STEP="build_openai_compat"
python3 scripts/build_openai_compat.py

CURRENT_STEP="validate_surface"
python3 scripts/validate_surface.py

CURRENT_STEP="validate_openai_compat"
python3 scripts/validate_openai_compat.py

CURRENT_STEP="generate_drift_reports"
python3 scripts/generate_drift_reports.py

CURRENT_STEP="lint_openapi"
python3 scripts/lint_openapi.py

CURRENT_STEP="validate_schema"
python3 scripts/validate_schema.py
