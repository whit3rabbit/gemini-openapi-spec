#!/usr/bin/env python3

from __future__ import annotations

from collections import defaultdict

from _gemini_common import (
    DOCS_DIR,
    DocOperation,
    OPENAPI_DIR,
    build_operation_id,
    load_doc_operations,
    normalize_google_path,
    read_json,
    singularize,
    write_json,
)
from native_schema_registry import apply_native_operation_overrides, build_native_components


def _derive_segment_pattern(pattern: str, openapi_name: str) -> str:
    """Derive the collection/*  segment for a specific parameter.

    For single-wildcard patterns like "models/*", returns the pattern
    as-is.  For multi-wildcard patterns like
    "fileSearchStores/*/documents/*", uses the singularization mapping
    to find which wildcard belongs to this openapi_name and returns just
    the relevant "collection/*" segment.
    """
    if not pattern:
        return ""
    segments = pattern.split("/")
    wildcards = [i for i, s in enumerate(segments) if s == "*"]
    if len(wildcards) <= 1:
        # Single wildcard: the whole pattern is the segment.
        return pattern
    # Multi-wildcard: find the literal segment before this parameter's
    # wildcard.  openapi_name is the singularized form of the literal
    # that precedes the wildcard.
    for wi in wildcards:
        if wi > 0:
            literal = segments[wi - 1]
            if singularize(literal) == openapi_name:
                return f"{literal}/*"
    # Fallback: return the full pattern.
    return pattern


def _load_tuning_supplemental_operations(discovery: dict) -> list[DocOperation]:
    """Load tunedModels operations from tuning reference pages and discovery."""
    supplemental: list[DocOperation] = []
    seen: set[tuple[str, str]] = set()

    # Doc-sourced: tuning reference and permissions reference
    for json_file in ("tuning-reference.json", "tuning-permissions-reference.json"):
        path = DOCS_DIR / json_file
        if not path.exists():
            continue
        data = read_json(path)
        for item in data.get("operations", []):
            key = (item["method"], item["normalized_path"])
            if key not in seen:
                seen.add(key)
                supplemental.append(
                    DocOperation(
                        resource=item["resource"],
                        name=item["name"],
                        method=item["method"],
                        raw_path=item["raw_path"],
                        normalized_path=item["normalized_path"],
                        description=item.get("description", ""),
                        path_parameters=item["path_parameters"],
                    )
                )

    # Discovery-sourced: CRUD operations not on the tuning reference pages
    if discovery:
        # Map discovery v1beta3 tunedModels paths to v1beta
        method_map = {"get": "GET", "post": "POST", "patch": "PATCH", "delete": "DELETE"}
        for raw_disc_path, path_item in discovery.get("paths", {}).items():
            if "tunedModels" not in raw_disc_path:
                continue
            # Normalize v1beta3 -> v1beta
            raw_path = raw_disc_path.replace("/v1beta3/", "/v1beta/")
            for http_method_lower, operation in path_item.items():
                if http_method_lower not in method_map:
                    continue
                http_method = method_map[http_method_lower]
                normalized_path, parameters = normalize_google_path(raw_path)
                key = (http_method, normalized_path)
                if key in seen:
                    continue
                seen.add(key)
                name = operation.get("x-google-operation-name", "")
                # PaLM was decommissioned but Google still ships GenerateText in
                # the discovery export. Drop it so it does not land in the spec.
                if name == "GenerateText":
                    continue
                if name.startswith("List"):
                    name = "list"
                elif name.startswith("Get"):
                    name = "get"
                elif name.startswith("Create"):
                    name = "create"
                elif name.startswith("Update"):
                    name = "patch"
                elif name.startswith("Delete"):
                    name = "delete"
                else:
                    # camelCase the operation name
                    name = name[0].lower() + name[1:] if name else http_method_lower

                if "/permissions" in raw_path:
                    resource = "v1beta.tunedModels.permissions"
                else:
                    resource = "v1beta.tunedModels"

                supplemental.append(
                    DocOperation(
                        resource=resource,
                        name=name,
                        method=http_method,
                        raw_path=raw_path,
                        normalized_path=normalized_path,
                        description=operation.get("description", ""),
                        path_parameters=parameters,
                    )
                )

    return supplemental


def build_spec() -> dict:
    operations = load_doc_operations()
    discovery = read_json(DOCS_DIR.parent / "discovery" / "openapi3_0.json")
    operations.extend(_load_tuning_supplemental_operations(discovery))
    paths: dict[str, dict] = defaultdict(dict)

    for operation in operations:
        parameters = []
        for parameter in operation.path_parameters:
            # Derive the per-parameter collection name from
            # segment_pattern (set by normalize_google_path for
            # multi-wildcard patterns) or by finding the openapi_name's
            # position in the full pattern.
            seg = parameter.get("segment_pattern")
            if not seg:
                # Compute from the full pattern and openapi_name.
                # For "models/*" with openapi_name "model", the
                # collection is "models".  For multi-wildcard patterns
                # like "fileSearchStores/*/documents/*", find the
                # literal segment that precedes this parameter's
                # wildcard.
                pat = parameter.get("pattern", "")
                oname = parameter["openapi_name"]
                seg = _derive_segment_pattern(pat, oname)
            if seg:
                collection = seg.rstrip("/*").rstrip("/")
                description = (
                    f"ID within the `{collection}` collection. "
                    f"Pass just the resource ID, not the full path"
                )
            else:
                description = "Google API path binding"
            if parameter["name"] != parameter["openapi_name"]:
                description += f". Original parameter name: `{parameter['name']}`"
            if parameter.get("binding_token"):
                description += f". Original binding token: `{{{parameter['binding_token']}}}`"
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
            if operation.normalized_path.startswith("/upload/"):
                request_body["description"] = (
                    "Google requires multipart/related or resumable upload "
                    "protocol. The content types shown here are a simplified "
                    "representation. See the Gemini Files API guide for the "
                    "actual upload flow."
                )

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
                "`all-methods` docs, with guide-documented extras and tuning reference "
                "endpoints added from their dedicated reference pages. Discovery-sourced "
                "CRUD operations for tunedModels are also included."
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
    print(f"Saved OpenAPI spec to {OPENAPI_DIR / 'gemini-native.openapi.json'}")


if __name__ == "__main__":
    main()
