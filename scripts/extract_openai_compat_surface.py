#!/usr/bin/env python3

from __future__ import annotations

import re
from collections import OrderedDict

from _gemini_common import DOCS_DIR, REPORTS_DIR, extract_text_lines, write_json

HOST_PREFIX = "https://generativelanguage.googleapis.com/v1beta/openai"
URL_RE = re.compile(r"https://generativelanguage\.googleapis\.com/v1beta/openai(/[A-Za-z0-9_./{}:-]+)")


def detect_method(lines: list[str], start: int) -> str:
    for index in range(start + 1, min(start + 20, len(lines))):
        line = lines[index]
        if line.startswith("curl "):
            break
        if line.startswith("-X "):
            return line.split()[1].upper()
        if line in {"-d", "-F"} or line.startswith("-d ") or line.startswith("-F "):
            return "POST"
    return "GET"


def normalize_path(path: str) -> str:
    if path.startswith("/models/") and path != "/models":
        return "/models/{model}"
    if path.startswith("/videos/") and path != "/videos":
        return "/videos/{video_id}"
    return path


def extract_url_from_curl(lines: list[str], index: int) -> str | None:
    line = lines[index]
    match = URL_RE.search(line)
    if match:
        return normalize_path(match.group(1))
    for next_index in range(index + 1, min(index + 4, len(lines))):
        match = URL_RE.search(lines[next_index])
        if match:
            return normalize_path(match.group(1))
    return None


def has_token_sequence(lines: list[str], tokens: list[str]) -> bool:
    token_count = len(tokens)
    for index in range(0, len(lines) - token_count + 1):
        if lines[index : index + token_count] == tokens:
            return True
    return False


def main() -> None:
    html = (DOCS_DIR / "openai-compat.html").read_text(encoding="utf-8")
    lines = extract_text_lines(html)

    explicit: OrderedDict[tuple[str, str], dict] = OrderedDict()
    for index, line in enumerate(lines):
        if line != "curl" and not line.startswith('curl "'):
            continue
        path = extract_url_from_curl(lines, index)
        if not path:
            continue
        method = detect_method(lines, index)
        explicit[(method, path)] = {
            "method": method,
            "path": path,
            "source_kind": "explicit_rest_example",
        }

    inferred = []
    sdk_checks = {
        "POST /batches": ["openai_client", ".", "batches", ".", "create", "("],
        "GET /batches/{batch_id}": ["client", ".", "batches", ".", "retrieve", "("],
    }
    for key, tokens in sdk_checks.items():
        if has_token_sequence(lines, tokens):
            method, path = key.split(" ", 1)
            inferred.append(
                {
                    "method": method,
                    "path": path,
                    "source_kind": "sdk_example_inferred_from_openai_contract",
                    "note": (
                        "Mentioned by Google OpenAI compatibility SDK example. "
                        "The page does not show a raw REST curl example for this route."
                    ),
                }
            )

    payload = {
        "explicit_rest_operations": list(explicit.values()),
        "sdk_inferred_operations": inferred,
        "explicit_rest_count": len(explicit),
        "sdk_inferred_count": len(inferred),
    }
    write_json(REPORTS_DIR / "openai-compat-surface.json", payload)
    print(f"Saved OpenAI compatibility surface report to {REPORTS_DIR / 'openai-compat-surface.json'}")


if __name__ == "__main__":
    main()
