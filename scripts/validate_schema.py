#!/usr/bin/env python3
"""Validate generated OpenAPI specs against the OpenAPI 3.1.0 JSON Schema.

The native spec is authored as 3.1.0 and validated strictly.
The compat spec inherits OpenAPI 3.0.0 from the upstream OpenAI snapshot,
so meta-schema validation is advisory only.
"""

from __future__ import annotations

import json
import urllib.request

from jsonschema import Draft202012Validator

from _gemini_common import OPENAPI_DIR, SOURCES_DIR

OPENAPI_31_SCHEMA_URL = "https://spec.openapis.org/oas/3.1/schema/2022-10-07"
CACHED_SCHEMA_PATH = SOURCES_DIR / "openapi-3.1-schema.json"


def fetch_meta_schema() -> dict:
    """Fetch the OpenAPI 3.1.0 meta-schema, caching locally."""
    if CACHED_SCHEMA_PATH.exists():
        return json.loads(CACHED_SCHEMA_PATH.read_text(encoding="utf-8"))

    with urllib.request.urlopen(OPENAPI_31_SCHEMA_URL) as response:
        schema = json.load(response)

    CACHED_SCHEMA_PATH.write_text(
        json.dumps(schema, indent=2) + "\n", encoding="utf-8"
    )
    return schema


def _validate(spec_path, validator) -> list:
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    return sorted(validator.iter_errors(spec), key=lambda e: list(e.path))


def _print_errors(errors, limit=10) -> None:
    for error in errors[:limit]:
        path = ".".join(str(p) for p in error.absolute_path)
        print(f"  - {path}: {error.message[:120]}")
    if len(errors) > limit:
        print(f"  ... and {len(errors) - limit} more")


def main() -> None:
    meta_schema = fetch_meta_schema()
    validator = Draft202012Validator(meta_schema)

    # Native spec: strict (3.1.0)
    native_path = OPENAPI_DIR / "gemini-native.openapi.json"
    native_errors = _validate(native_path, validator)
    if native_errors:
        print(f"FAIL {native_path.name}: {len(native_errors)} schema violation(s)")
        _print_errors(native_errors)
        raise SystemExit(1)
    print(f"PASS {native_path.name}")

    # Compat spec: advisory (upstream declares 3.0.0, not 3.1.0)
    compat_path = OPENAPI_DIR / "gemini-openai-compat.openapi.json"
    compat_errors = _validate(compat_path, validator)
    if compat_errors:
        print(
            f"ADVISORY {compat_path.name}: {len(compat_errors)} issue(s) "
            f"(upstream spec is OpenAPI 3.0.0, not 3.1.0)"
        )
        _print_errors(compat_errors)
    else:
        print(f"PASS {compat_path.name}")


if __name__ == "__main__":
    main()
