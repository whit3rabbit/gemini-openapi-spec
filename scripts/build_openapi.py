#!/usr/bin/env python3

from __future__ import annotations

from collections import defaultdict

from _gemini_common import (
    DOCS_DIR,
    OPENAPI_DIR,
    build_operation_id,
    load_doc_operations,
    read_json,
    write_json,
)
from native_schema_registry import apply_native_operation_overrides, build_native_components


def build_spec() -> dict:
    operations = load_doc_operations()
    discovery = read_json(DOCS_DIR.parent / "discovery" / "openapi3_0.json")
    paths: dict[str, dict] = defaultdict(dict)

    for operation in operations:
        parameters = []
        for parameter in operation.path_parameters:
            description = "Google API path binding"
            if parameter["pattern"]:
                description = f"Google API path binding, expected pattern `{parameter['pattern']}`"
            if parameter["name"] != parameter["openapi_name"]:
                description = f"{description}. Original parameter name: `{parameter['name']}`"
            if parameter.get("binding_token"):
                description = f"{description}. Original binding token: `{{{parameter['binding_token']}}}`"
            parameters.append(
                {
                    "name": parameter["openapi_name"],
                    "in": "path",
                    "required": True,
                    "description": description,
                    "schema": {"type": "string"},
                }
            )

        request_body = None
        if operation.method in {"POST", "PATCH"}:
            content = {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/GenericJsonObject"}
                }
            }
            if operation.normalized_path.startswith("/upload/"):
                content["application/octet-stream"] = {
                    "schema": {"type": "string", "format": "binary"}
                }
            request_body = {
                "required": False,
                "content": content,
            }

        responses = {
            "200": {
                "description": "Successful response",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/GenericJsonObject"}
                    }
                },
            }
        }

        if operation.normalized_path.startswith("/upload/"):
            responses["200"]["content"]["application/octet-stream"] = {
                "schema": {"type": "string", "format": "binary"}
            }

        path_item = {
            "tags": [operation.resource],
            "operationId": build_operation_id(operation),
            "summary": operation.name,
            "description": operation.description or f"{operation.name} on {operation.resource}",
            "security": [{"ApiKeyAuth": []}],
            "x-google-original-path": operation.raw_path,
            "parameters": parameters,
            "responses": responses,
        }
        if request_body is not None:
            path_item["requestBody"] = request_body

        path_item, extra_paths = apply_native_operation_overrides(operation, path_item)

        paths[operation.normalized_path][operation.method.lower()] = path_item
        for extra_path, extra_path_item in extra_paths:
            paths[extra_path][operation.method.lower()] = extra_path_item

    return {
        "openapi": "3.1.0",
        "info": {
            "title": "Gemini Developer API",
            "version": "v1beta",
            "description": (
                "Generated working OpenAPI spec for the documented Gemini Developer API "
                "surface. Path and method coverage come primarily from the live "
                "`all-methods` docs, with selected guide-documented extras added where "
                "the official Gemini guides publish native routes that are not listed in "
                "the method index. Raw upstream discovery output is kept separately because "
                "it currently describes an older, smaller `v1beta3` surface."
            ),
            "x-upstream-discovery-version": discovery["info"]["version"],
            "x-upstream-discovery-revision": discovery["info"].get("x-google-revision"),
        },
        "servers": [
            {
                "url": "https://generativelanguage.googleapis.com",
                "description": "Gemini Developer API",
            }
        ],
        "security": [{"ApiKeyAuth": []}],
        "externalDocs": {
            "description": "Gemini API reference",
            "url": "https://ai.google.dev/api",
        },
        "paths": dict(sorted(paths.items())),
        "components": {
            "securitySchemes": {
                "ApiKeyAuth": {
                    "type": "apiKey",
                    "in": "header",
                    "name": "x-goog-api-key",
                    "description": "Gemini Developer API key",
                }
            },
            "schemas": {
                "GenericJsonObject": {
                    "type": "object",
                    "description": (
                        "Placeholder schema. This repo only promotes request and response "
                        "shapes to concrete schemas when they are verified against a current "
                        "machine-readable upstream source."
                    ),
                    "additionalProperties": True,
                },
                **build_native_components(),
            },
        },
    }


def main() -> None:
    spec = build_spec()
    write_json(OPENAPI_DIR / "gemini-native.openapi.json", spec)
    # Legacy alias kept for external consumers that may reference this filename.
    write_json(OPENAPI_DIR / "gemini-api.openapi.json", spec)
    print(f"Saved OpenAPI spec to {OPENAPI_DIR / 'gemini-native.openapi.json'}")


if __name__ == "__main__":
    main()
