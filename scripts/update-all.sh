#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$repo_root"

python3 scripts/refresh_sources.py
python3 scripts/extract_python_genai_surface.py
python3 scripts/build_openapi.py
python3 scripts/extract_openai_compat_surface.py
python3 scripts/build_openai_compat.py
python3 scripts/validate_surface.py
python3 scripts/validate_openai_compat.py
python3 scripts/generate_drift_reports.py
python3 scripts/lint_openapi.py
