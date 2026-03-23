#!/usr/bin/env python3

from __future__ import annotations

import os
import re
import subprocess

from _gemini_common import OPENAPI_DIR, REPORTS_DIR, write_json

REDOCLY_VERSION = "2.24.1"

NATIVE_SKIP_RULES = [
    "operation-4xx-response",
    "info-license",
]

COMPAT_SKIP_RULES = [
    "operation-4xx-response",
    "info-license",
    "no-unused-components",
    "no-invalid-schema-examples",
    "no-required-schema-properties-undefined",
]


def _lint(spec_path: str, skip_rules: list[str]) -> dict:
    command = [
        "npx",
        "--yes",
        f"@redocly/cli@{REDOCLY_VERSION}",
        "lint",
        spec_path,
        *[item for rule in skip_rules for item in ("--skip-rule", rule)],
    ]
    env = {**os.environ, "NO_COLOR": "1"}
    result = subprocess.run(command, capture_output=True, text=True, env=env)
    combined_output = (result.stdout + "\n" + result.stderr).strip()
    match = re.search(r"Validation failed with (\d+) errors?(?: and (\d+) warnings?)?", combined_output)
    warning_match = re.search(
        r"Validation failed with \d+ errors?(?: and (\d+) warnings?)?", combined_output
    )
    warning_group = warning_match.group(1) if warning_match else None
    return {
        "exit_code": result.returncode,
        "error_count": int(match.group(1)) if match else 0,
        "warning_count": int(warning_group) if warning_group is not None else 0,
        "output_excerpt": "\n".join(
            line for line in combined_output.splitlines()[:80]
            if not re.match(r".*validated in \d+ms", line)
        ),
    }


def main() -> None:
    native_result = _lint(str(OPENAPI_DIR / "gemini-native.openapi.json"), NATIVE_SKIP_RULES)
    compat_result = _lint(
        str(OPENAPI_DIR / "gemini-openai-compat.openapi.json"), COMPAT_SKIP_RULES
    )

    report = {
        "redocly_version": REDOCLY_VERSION,
        "native": native_result,
        "compat": {
            **compat_result,
            "mode": "advisory",
            "note": (
                "Compat lint is advisory only. The copied upstream OpenAI spec currently "
                "fails Redocly on schema-level issues that are not introduced by this repo."
            ),
        },
    }
    write_json(REPORTS_DIR / "openapi-lint-report.json", report)

    if native_result["exit_code"] != 0:
        print(native_result["output_excerpt"])
        raise SystemExit(native_result["exit_code"])

    print("Native OpenAPI lint passed")
    if compat_result["exit_code"] != 0:
        print("Compat OpenAPI lint reported advisory failures")
    else:
        print("Compat OpenAPI lint passed")


if __name__ == "__main__":
    main()
