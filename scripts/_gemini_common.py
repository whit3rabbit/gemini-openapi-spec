#!/usr/bin/env python3

from __future__ import annotations

import json
import re
import subprocess
import urllib.request
from dataclasses import dataclass
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
SOURCES_DIR = ROOT / "sources"
DOCS_DIR = SOURCES_DIR / "docs"
DISCOVERY_DIR = SOURCES_DIR / "discovery"
REPORTS_DIR = ROOT / "reports"
OPENAPI_DIR = ROOT / "openapi"
OPENAI_DIR = SOURCES_DIR / "openai"

DISCOVERY_URL = "https://generativelanguage.googleapis.com/$discovery/OPENAPI3_0"
ALL_METHODS_URL = "https://ai.google.dev/api/all-methods"
FILES_GUIDE_URL = "https://ai.google.dev/gemini-api/docs/files"
BATCH_GUIDE_URL = "https://ai.google.dev/gemini-api/docs/batch-api"
MODELS_REF_URL = "https://ai.google.dev/api/models"
TOKENS_REF_URL = "https://ai.google.dev/api/tokens"
PALM_REF_URL = "https://ai.google.dev/api/palm"
GENERATE_CONTENT_REF_URL = "https://ai.google.dev/api/generate-content"
FILE_SEARCH_STORES_REF_URL = "https://ai.google.dev/api/file-search/file-search-stores"
FILE_SEARCH_DOCUMENTS_REF_URL = "https://ai.google.dev/api/file-search/documents"
OPENAI_COMPAT_URL = "https://ai.google.dev/gemini-api/docs/openai"
OPENAI_UPSTREAM_SPEC_URL = (
    "https://raw.githubusercontent.com/openai/openai-openapi/manual_spec/openapi.yaml"
)


@dataclass(frozen=True)
class DocOperation:
    resource: str
    name: str
    method: str
    raw_path: str
    normalized_path: str
    description: str
    path_parameters: list[dict[str, str]]

    def to_json(self) -> dict[str, Any]:
        return {
            "resource": self.resource,
            "name": self.name,
            "method": self.method,
            "raw_path": self.raw_path,
            "normalized_path": self.normalized_path,
            "description": self.description,
            "path_parameters": self.path_parameters,
        }


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        data = data.strip()
        if data:
            self.parts.append(unescape(data))


def ensure_dirs() -> None:
    for path in (DOCS_DIR, DISCOVERY_DIR, REPORTS_DIR, OPENAPI_DIR, OPENAI_DIR):
        path.mkdir(parents=True, exist_ok=True)


def fetch_text(url: str) -> str:
    with urllib.request.urlopen(url) as response:
        return response.read().decode("utf-8", "replace")


def fetch_json(url: str) -> dict[str, Any]:
    with urllib.request.urlopen(url) as response:
        return json.load(response)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def slugify_resource(resource: str) -> str:
    return resource.replace(".", "_")


def normalize_google_path(path: str) -> tuple[str, list[dict[str, str]]]:
    parameters: list[dict[str, str]] = []

    def sanitize(value: str) -> str:
        sanitized = re.sub(r"[^A-Za-z0-9_]+", "_", value).strip("_")
        return sanitized or "param"

    def singularize(value: str) -> str:
        if value.endswith("ies") and len(value) > 3:
            return value[:-3] + "y"
        for suffix in ("ches", "shes", "xes", "zes", "ses"):
            if value.endswith(suffix) and len(value) > len(suffix):
                return value[: -2]
        if value.endswith("s") and not value.endswith("ss") and len(value) > 1:
            return value[:-1]
        return value

    def replace(match: re.Match[str]) -> str:
        token = match.group(1)
        if "=" in token:
            name, pattern = token.split("=", 1)
        else:
            name, pattern = token, ""
        if not pattern:
            openapi_name = sanitize(name)
            parameters.append(
                {
                    "name": name,
                    "pattern": pattern,
                    "openapi_name": openapi_name,
                    "binding_token": token,
                }
            )
            return "{" + openapi_name + "}"

        pattern_segments = [segment for segment in pattern.split("/") if segment]
        if not pattern_segments:
            openapi_name = sanitize(name)
            parameters.append(
                {
                    "name": name,
                    "pattern": pattern,
                    "openapi_name": openapi_name,
                    "binding_token": token,
                }
            )
            return "{" + openapi_name + "}"

        rebuilt_segments: list[str] = []
        literal_segments: list[str] = []
        wildcard_name_counts: dict[str, int] = {}

        for segment in pattern_segments:
            if segment == "*":
                context = literal_segments[-1] if literal_segments else name
                base_name = sanitize(singularize(context))
                occurrence = wildcard_name_counts.get(base_name, 0) + 1
                wildcard_name_counts[base_name] = occurrence
                openapi_name = base_name if occurrence == 1 else f"{base_name}_{occurrence}"
                parameters.append(
                    {
                        "name": name,
                        "pattern": pattern,
                        "openapi_name": openapi_name,
                        "binding_token": token,
                    }
                )
                rebuilt_segments.append("{" + openapi_name + "}")
                continue

            literal_segments.append(segment)
            rebuilt_segments.append(segment)

        if not wildcard_name_counts:
            return "/".join(rebuilt_segments)

        return "/".join(rebuilt_segments)

    normalized = re.sub(r"\{([^}]+)\}", replace, path)
    return normalized, parameters


def parse_all_methods_html(html: str) -> list[DocOperation]:
    parser = _TextExtractor()
    parser.feed(html)
    lines = parser.parts
    operations: list[DocOperation] = []
    resource: str | None = None
    index = 0

    while index < len(lines):
        line = lines[index]
        if line == "REST Resource:" and index + 1 < len(lines):
            resource = lines[index + 1]
            index += 2
            if index < len(lines) and lines[index] == "Methods":
                index += 1
            continue

        match = re.match(r"^(GET|POST|PATCH|DELETE)\s+(/\S+)$", line)
        if resource and index >= 1 and match:
            name = lines[index - 1]
            raw_path = match.group(2)
            normalized_path, parameters = normalize_google_path(raw_path)
            description = lines[index + 1] if index + 1 < len(lines) else ""
            operations.append(
                DocOperation(
                    resource=resource,
                    name=name,
                    method=match.group(1),
                    raw_path=raw_path,
                    normalized_path=normalized_path,
                    description=description,
                    path_parameters=parameters,
                )
            )
            index += 2
            continue

        index += 1

    return operations


def extract_text_lines(html: str) -> list[str]:
    parser = _TextExtractor()
    parser.feed(html)
    return parser.parts


def parse_files_guide_html(html: str) -> dict[str, Any]:
    lines = extract_text_lines(html)

    upload_match = re.search(r"(?P<path>/upload/v1beta/files)\b", html)
    upload_aliases: list[dict[str, str]] = []
    if upload_match:
        upload_aliases.append(
            {
                "path": upload_match.group("path"),
                "evidence": upload_match.group(0),
            }
        )

    download_evidence = next(
        (line for line in lines if "can't download the files" in line),
        None,
    )

    return {
        "source": FILES_GUIDE_URL,
        "documented_aliases": upload_aliases,
        "download_policy": {
            "download_allowed": False if download_evidence else None,
            "evidence": download_evidence,
        },
    }


def parse_batch_guide_html(html: str) -> dict[str, Any]:
    lines = extract_text_lines(html)
    documented_operations: list[dict[str, Any]] = []

    download_evidence = None
    for index in range(len(lines) - 4):
        if (
            lines[index] == "https://generativelanguage.googleapis.com/download/v1beta/"
            and lines[index + 1] == "$responses_file_name"
            and lines[index + 2] == ":download?alt"
            and lines[index + 3] == "="
            and lines[index + 4] == "media"
        ):
            download_evidence = "/download/v1beta/$responses_file_name:download?alt=media"
            break

    if download_evidence:
        documented_operations.append(
            {
                "method": "GET",
                "normalized_path": "/download/v1beta/files/{file}:download",
                "query_parameters": [
                    {
                        "name": "alt",
                        "required": True,
                        "schema": {"type": "string", "enum": ["media"]},
                    }
                ],
                "response_content_type": "application/octet-stream",
                "evidence": download_evidence,
                "notes": (
                    "Batch results download for generated response files. The guide uses "
                    "`$responses_file_name`, whose value is a file resource name."
                ),
            }
        )

    delete_alias_evidence = None
    for index in range(len(lines) - 2):
        if (
            lines[index] == "https://generativelanguage.googleapis.com/v1beta/"
            and lines[index + 1] == "$BATCH_NAME"
            and lines[index + 2] == ":delete"
        ):
            delete_alias_evidence = "/v1beta/$BATCH_NAME:delete"
            break

    return {
        "source": BATCH_GUIDE_URL,
        "documented_operations": documented_operations,
        "questionable_examples": (
            [
                {
                    "kind": "batch_delete_alias",
                    "evidence": delete_alias_evidence,
                    "notes": (
                        "The Batch guide shows a `:delete` REST example, while the API "
                        "reference lists `DELETE /v1beta/batches/{batch}`."
                    ),
                }
            ]
            if delete_alias_evidence
            else []
        ),
    }


def parse_models_reference_html(html: str) -> dict[str, Any]:
    lines = extract_text_lines(html)
    last_updated = next(
        (line for line in lines if line.startswith("Last updated ")),
        None,
    )
    return {
        "source": MODELS_REF_URL,
        "last_updated": last_updated,
    }


def parse_tokens_reference_html(html: str) -> dict[str, Any]:
    lines = extract_text_lines(html)
    last_updated = next(
        (line for line in lines if line.startswith("Last updated ")),
        None,
    )
    return {
        "source": TOKENS_REF_URL,
        "last_updated": last_updated,
    }


def parse_palm_reference_html(html: str) -> dict[str, Any]:
    lines = extract_text_lines(html)
    last_updated = next(
        (line for line in lines if line.startswith("Last updated ")),
        None,
    )
    documented_legacy_methods = [
        method
        for method in [
            "models.countTextTokens",
            "models.countMessageTokens",
            "models.embedText",
            "models.batchEmbedText",
            "models.generateText",
            "models.generateMessage",
        ]
        if method in html
    ]
    return {
        "source": PALM_REF_URL,
        "last_updated": last_updated,
        "documented_legacy_methods": documented_legacy_methods,
    }


def parse_generate_content_reference_html(html: str) -> dict[str, Any]:
    lines = extract_text_lines(html)
    last_updated = next(
        (line for line in lines if line.startswith("Last updated ")),
        None,
    )
    stream_response_evidence = None
    stream_response_html_marker = "response body contains a stream of"
    stream_response_html_index = html.find(stream_response_html_marker)
    if stream_response_html_index != -1 and "GenerateContentResponse" in html[
        stream_response_html_index : stream_response_html_index + 400
    ]:
        stream_response_evidence = "response body contains a stream of GenerateContentResponse instances"
    alt_sse_evidence = (
        "alt=sse"
        if "streamGenerateContent?alt=sse" in html
        else None
    )
    return {
        "source": GENERATE_CONTENT_REF_URL,
        "last_updated": last_updated,
        "stream_generate_content": {
            "event_stream_response_evidence": stream_response_evidence,
            "alt_sse_evidence": alt_sse_evidence,
        },
    }


def parse_file_search_stores_reference_html(html: str) -> dict[str, Any]:
    upload_aliases: list[dict[str, str]] = []
    if "/api/rest/v1beta/media/uploadToFileSearchStore" in html:
        upload_aliases.append(
            {
                "raw_path": "/upload/v1beta/{fileSearchStoreName=fileSearchStores/*}:uploadToFileSearchStore",
                "normalized_path": "/upload/v1beta/fileSearchStores/{fileSearchStore}:uploadToFileSearchStore",
                "method": "POST",
                "evidence": "/api/rest/v1beta/media/uploadToFileSearchStore",
            }
        )

    return {
        "source": FILE_SEARCH_STORES_REF_URL,
        "documented_aliases": upload_aliases,
    }


def parse_file_search_documents_reference_html(html: str) -> dict[str, Any]:
    lines = extract_text_lines(html)
    last_updated = next(
        (line for line in lines if line.startswith("Last updated ")),
        None,
    )

    return {
        "source": FILE_SEARCH_DOCUMENTS_REF_URL,
        "documented_aliases": [],
        "last_updated": last_updated,
    }


def load_doc_operations() -> list[DocOperation]:
    payload = read_json(DOCS_DIR / "all-methods.json")
    return [
        DocOperation(
            resource=item["resource"],
            name=item["name"],
            method=item["method"],
            raw_path=item["raw_path"],
            normalized_path=item["normalized_path"],
            description=item["description"],
            path_parameters=item["path_parameters"],
        )
        for item in payload["operations"]
    ]


def load_files_guide_evidence() -> dict[str, Any]:
    return read_json(DOCS_DIR / "files-guide.json")


def load_batch_guide_evidence() -> dict[str, Any]:
    return read_json(DOCS_DIR / "batch-guide.json")


def load_generate_content_reference_evidence() -> dict[str, Any]:
    return read_json(DOCS_DIR / "generate-content-reference.json")


def load_file_search_stores_reference_evidence() -> dict[str, Any]:
    return read_json(DOCS_DIR / "file-search-stores-reference.json")


def build_operation_id(operation: DocOperation) -> str:
    resource = slugify_resource(operation.resource)
    return f"{resource}_{operation.name}"


def canonical_operation_key(method: str, path: str) -> str:
    return f"{method.upper()} {path}"


def load_yaml_via_ruby(path: Path) -> Any:
    ruby_program = """
require 'json'
require 'yaml'
payload = YAML.safe_load(File.read(ARGV[0]), aliases: true)
puts JSON.generate(payload)
"""
    result = subprocess.run(
        ["ruby", "-e", ruby_program, str(path)],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)
