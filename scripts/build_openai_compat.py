#!/usr/bin/env python3

from __future__ import annotations

from copy import deepcopy

from _gemini_common import (
    OPENAI_DIR,
    OPENAPI_DIR,
    REPORTS_DIR,
    canonical_operation_key,
    load_yaml_via_ruby,
    read_json,
    write_json,
)


def _copy_path_item(openai_spec: dict, path: str, method: str) -> tuple[str, dict] | None:
    upstream_path_item = openai_spec.get("paths", {}).get(path)
    if not upstream_path_item:
        return None
    operation = upstream_path_item.get(method.lower())
    if not operation:
        return None
    return path, {method.lower(): deepcopy(operation)}


def _generic_json_response() -> dict:
    return {
        "description": "Successful response",
        "content": {
            "application/json": {
                "schema": {"$ref": "#/components/schemas/GenericJsonObject"}
            }
        },
    }


def _generic_json_request(required: bool = True) -> dict:
    return {
        "required": required,
        "content": {
            "application/json": {
                "schema": {"$ref": "#/components/schemas/GenericJsonObject"}
            }
        },
    }


def _gemini_extra_body_ref(name: str) -> dict:
    return {"$ref": f"#/components/schemas/{name}"}


def _enum_string_schema(values: list[str], description: str | None = None) -> dict:
    schema = {"type": "string", "enum": values}
    if description:
        schema["description"] = description
    return schema


def _strip_openai_enums(schemas: dict) -> None:
    """Replace inline OpenAI-specific enums with open string types.

    Covers model enums on embeddings/images, voice enums, and batch
    endpoint enums that are defined inline rather than via $ref to
    ModelIdsShared (which is handled separately).
    """
    # Embedding model enum (text-embedding-ada-002 etc.)
    emb = schemas.get("CreateEmbeddingRequest", {}).get("properties", {})
    if "model" in emb:
        emb["model"] = {
            "type": "string",
            "description": (
                "Model ID for embeddings. For Gemini, use "
                "'text-embedding-004' or 'gemini-embedding-001'."
            ),
            "example": "text-embedding-004",
        }

    # Image model enum (dall-e-2, dall-e-3, gpt-image-1)
    img = schemas.get("CreateImageRequest", {}).get("properties", {})
    if "model" in img:
        img["model"] = {
            "type": "string",
            "description": (
                "Model ID for image generation. For Gemini, use "
                "'imagen-3.0-generate-002' or similar."
            ),
            "example": "imagen-3.0-generate-002",
            "nullable": True,
        }

    # Voice enum (alloy, ash, echo, etc.)
    if "VoiceIdsShared" in schemas:
        schemas["VoiceIdsShared"] = {
            "type": "string",
            "description": (
                "Voice ID. For Gemini, use Gemini voice names such as "
                "'Aoede', 'Charon', 'Fenrir', 'Kore', or 'Puck'. "
                "Upstream OpenAI voice values are not applicable."
            ),
            "example": "Kore",
        }

    # Batch endpoint enum is handled inline on the path operation in
    # build_spec() since the upstream spec inlines the schema rather
    # than referencing CreateBatchRequest.


def _collect_refs(obj: object, _acc: set[str] | None = None) -> set[str]:
    """Recursively collect all $ref target names from a JSON-like structure."""
    if _acc is None:
        _acc = set()
    prefix = "#/components/schemas/"
    if isinstance(obj, dict):
        ref = obj.get("$ref")
        if isinstance(ref, str) and ref.startswith(prefix):
            _acc.add(ref[len(prefix):])
        for v in obj.values():
            _collect_refs(v, _acc)
    elif isinstance(obj, list):
        for item in obj:
            _collect_refs(item, _acc)
    return _acc


def _prune_unreachable_schemas(spec: dict) -> int:
    """Remove schemas not reachable from paths or Gemini-added schemas.

    Returns the number of schemas removed.
    """
    schemas = spec.get("components", {}).get("schemas", {})
    if not schemas:
        return 0

    # Seed reachable set from all paths (operations, parameters, responses, extensions)
    reachable: set[str] = set()
    queue: list[str] = []

    # Collect refs from paths
    path_refs = _collect_refs(spec.get("paths", {}))
    for name in path_refs:
        if name in schemas and name not in reachable:
            reachable.add(name)
            queue.append(name)

    # Also seed Gemini-specific schemas (they use vendor extensions not always in paths)
    for name in list(schemas):
        if name.startswith("Gemini") or name == "GenericJsonObject":
            if name not in reachable:
                reachable.add(name)
                queue.append(name)

    # BFS: follow $refs from reachable schemas
    while queue:
        current = queue.pop()
        schema = schemas.get(current)
        if schema is None:
            continue
        for ref_name in _collect_refs(schema):
            if ref_name in schemas and ref_name not in reachable:
                reachable.add(ref_name)
                queue.append(ref_name)

    # Remove unreachable
    unreachable = set(schemas) - reachable
    for name in unreachable:
        del schemas[name]

    return len(unreachable)


def build_spec() -> tuple[dict, dict]:
    openai_spec = load_yaml_via_ruby(OPENAI_DIR / "openapi.yaml")
    compat_surface = read_json(REPORTS_DIR / "openai-compat-surface.json")

    paths: dict[str, dict] = {}
    copied_from_upstream: list[str] = []
    missing_from_upstream: list[str] = []

    for item in compat_surface["explicit_rest_operations"]:
        copied = _copy_path_item(openai_spec, item["path"], item["method"])
        if copied is None:
            missing_from_upstream.append(f"{item['method']} {item['path']}")
            continue
        path, path_item = copied
        method = item["method"].lower()
        path_item[method]["x-gemini-compat-source"] = item["source_kind"]
        paths[path] = {**paths.get(path, {}), **path_item}
        copied_from_upstream.append(f"{item['method']} {item['path']}")

    for item in compat_surface["sdk_inferred_operations"]:
        copied = _copy_path_item(openai_spec, item["path"], item["method"])
        if copied is None:
            missing_from_upstream.append(f"{item['method']} {item['path']}")
            continue
        path, path_item = copied
        method = item["method"].lower()
        path_item[method]["x-gemini-compat-source"] = item["source_kind"]
        path_item[method]["x-gemini-compat-note"] = item["note"]
        paths[path] = {**paths.get(path, {}), **path_item}
        copied_from_upstream.append(f"{item['method']} {item['path']}")

    # Issue 4A: note that batch input files come from the native Files API
    batches_post = paths.get("/batches", {}).get("post")
    if batches_post:
        batches_post["x-gemini-compat-note"] = (
            "Batch input files must be uploaded via the Gemini native Files "
            "API (POST /upload/v1beta/files). The OpenAI /files endpoint is "
            "not supported. Pass the Gemini file resource URI as input_file_id."
        )
        # Strip the inline endpoint enum (/v1/chat/completions etc.) from
        # the batch request body -- it's defined inline, not in a named schema.
        try:
            props = batches_post["requestBody"]["content"]["application/json"]["schema"]["properties"]
            if "endpoint" in props and "enum" in props["endpoint"]:
                props["endpoint"] = {
                    "type": "string",
                    "description": (
                        "API endpoint for batch requests. For Gemini, use the "
                        "OpenAI-compatible endpoint paths supported by the "
                        "Gemini batch API."
                    ),
                }
        except (KeyError, TypeError):
            pass

    paths["/videos"] = {
        "post": {
            "tags": ["videos"],
            "operationId": "videos_create",
            "summary": "Generate video",
            "description": "Gemini OpenAI-compatible video generation endpoint documented by Google.",
            "security": [{"BearerAuth": []}],
            "x-gemini-compat-source": "explicit_rest_example",
            "x-gemini-compat-delta": "gemini_only_not_in_openai_upstream_spec",
            "requestBody": {
                "required": True,
                "content": {
                    "multipart/form-data": {
                        "schema": {
                            "type": "object",
                            "additionalProperties": True,
                            "properties": {
                                "model": {"type": "string"},
                                "prompt": {"type": "string"},
                                "google": {
                                    "type": "string",
                                    "description": (
                                        "JSON-encoded Gemini-specific video "
                                        "options (aspect ratio, resolution, "
                                        "etc.). See GeminiVideosGoogleOptions "
                                        "for structure."
                                    ),
                                },
                            },
                            "required": ["model", "prompt"],
                        }
                    }
                },
            },
            "responses": {"200": _generic_json_response()},
        }
    }
    paths["/videos/{video_id}"] = {
        "get": {
            "tags": ["videos"],
            "operationId": "videos_retrieve",
            "summary": "Get video status",
            "description": "Poll a previously created video generation request.",
            "security": [{"BearerAuth": []}],
            "x-gemini-compat-source": "explicit_rest_example",
            "x-gemini-compat-delta": "gemini_only_not_in_openai_upstream_spec",
            "parameters": [
                {
                    "name": "video_id",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string"},
                }
            ],
            "responses": {"200": _generic_json_response()},
        }
    }

    components = deepcopy(openai_spec.get("components", {}))
    security_schemes = components.setdefault("securitySchemes", {})
    if "BearerAuth" not in security_schemes:
        security_schemes["BearerAuth"] = {"type": "http", "scheme": "bearer"}
    schemas = components.setdefault("schemas", {})

    # Replace upstream OpenAI model enums with a plain string type.
    # The anyOf already accepted any string, but the enum values
    # (gpt-4o, dall-e-3, etc.) are misleading for Gemini users.
    for model_schema_name in ("ModelIdsShared", "ModelIdsResponses"):
        if model_schema_name in schemas:
            schemas[model_schema_name] = {
                "type": "string",
                "description": (
                    "Model ID. For the Gemini API, use Gemini model names "
                    "such as 'gemini-2.5-flash' or 'gemini-2.5-pro'. "
                    "Upstream OpenAI enum values are not applicable."
                ),
                "example": "gemini-2.5-flash",
            }

    # Strip remaining inline OpenAI-specific enums that bypass the
    # top-level schema replacement above.
    _strip_openai_enums(schemas)

    schemas["GenericJsonObject"] = {
        "type": "object",
        "description": "Placeholder schema for Gemini OpenAI-compatible responses or requests not modeled by the upstream OpenAI spec.",
        "additionalProperties": True,
    }
    schemas["GeminiThinkingConfig"] = {
        "type": "object",
        "properties": {
            "thinking_level": _enum_string_schema(
                ["minimal", "low", "medium", "high"],
                "Reasoning level documented on the Gemini OpenAI compatibility page.",
            ),
            "thinking_budget": {"type": "integer", "minimum": 0},
            "include_thoughts": {"type": "boolean"},
        },
        "additionalProperties": False,
    }
    schemas["GeminiChatGoogleOptions"] = {
        "type": "object",
        "properties": {
            "cached_content": {
                "type": "string",
                "pattern": "^cachedContents/[^/]+$",
                "description": "Gemini cached content resource name.",
            },
            "thinking_config": _gemini_extra_body_ref("GeminiThinkingConfig"),
        },
        "additionalProperties": False,
    }
    schemas["GeminiChatExtraBody"] = {
        "type": "object",
        "properties": {
            "google": _gemini_extra_body_ref("GeminiChatGoogleOptions"),
        },
        "additionalProperties": False,
    }
    schemas["GeminiImageGenerationConfig"] = {
        "type": "object",
        "properties": {
            "responseModalities": {
                "type": "array",
                "items": _enum_string_schema(["IMAGE"]),
            },
            "candidateCount": {"type": "integer", "minimum": 1},
        },
        "description": "Partial Gemini image generation config documented by example on the compatibility page.",
        "additionalProperties": True,
    }
    schemas["GeminiImageSafetySetting"] = {
        "type": "object",
        "properties": {
            "category": {"type": "string"},
            "threshold": {"type": "string"},
        },
        "additionalProperties": False,
    }
    schemas["GeminiImageGoogleSearchTool"] = {
        "type": "object",
        "properties": {
            "google_search": {"type": "object", "additionalProperties": False},
        },
        "required": ["google_search"],
        "additionalProperties": False,
    }
    schemas["GeminiImagesGoogleOptions"] = {
        "type": "object",
        "properties": {
            "aspect_ratio": _enum_string_schema(
                ["16:9", "1:1", "9:16"],
                "Documented examples from the Gemini OpenAI compatibility page.",
            ),
            "generation_config": _gemini_extra_body_ref("GeminiImageGenerationConfig"),
            "safety_settings": {
                "type": "array",
                "items": _gemini_extra_body_ref("GeminiImageSafetySetting"),
            },
            "tools": {
                "type": "array",
                "items": _gemini_extra_body_ref("GeminiImageGoogleSearchTool"),
            },
        },
        "additionalProperties": False,
    }
    schemas["GeminiImagesExtraBody"] = {
        "type": "object",
        "properties": {
            "google": _gemini_extra_body_ref("GeminiImagesGoogleOptions"),
        },
        "additionalProperties": False,
    }
    schemas["GeminiVideoReferenceImage"] = {
        "type": "object",
        "properties": {
            "data": {"type": "string", "description": "Base64-encoded image content."},
            "mime_type": {"type": "string"},
        },
        "required": ["data"],
        "additionalProperties": False,
    }
    schemas["GeminiVideoLastFrame"] = {
        "type": "object",
        "properties": {
            "data": {"type": "string", "description": "Base64-encoded image content."},
            "mime_type": {"type": "string"},
        },
        "required": ["data"],
        "additionalProperties": False,
    }
    schemas["GeminiVideosGoogleOptions"] = {
        "type": "object",
        "properties": {
            "aspect_ratio": _enum_string_schema(
                ["16:9", "9:16"],
                "Documented video aspect ratios on the Gemini OpenAI compatibility page.",
            ),
            "resolution": _enum_string_schema(["720p", "1080p", "4K"]),
            "duration_seconds": {"type": "integer", "enum": [4, 6, 8]},
            "frame_rate": {
                "type": "string",
                "pattern": "^[0-9]+$",
                "description": "String-valued frame rate, for example \"24\".",
            },
            "input_reference": {"type": "string"},
            "extend_video_id": {"type": "string"},
            "negative_prompt": {"type": "string"},
            "seed": {"type": "integer"},
            "style": _enum_string_schema(["cinematic", "creative"]),
            "person_generation": _enum_string_schema(
                ["allow_adult", "allow_all", "dont_allow"]
            ),
            "reference_images": {
                "type": "array",
                "items": _gemini_extra_body_ref("GeminiVideoReferenceImage"),
                "maxItems": 3,
            },
            "image": {"type": "string", "description": "Base64-encoded initial input image."},
            "last_frame": _gemini_extra_body_ref("GeminiVideoLastFrame"),
        },
        "additionalProperties": False,
    }
    schemas["GeminiVideosExtraBody"] = {
        "type": "object",
        "properties": {
            "google": _gemini_extra_body_ref("GeminiVideosGoogleOptions"),
        },
        "additionalProperties": False,
    }
    schemas["GeminiVideoOperation"] = {
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "status": {
                "type": "string",
                "description": (
                    "Google explicitly shows `processing` in the create example. "
                    "Other terminal states are not enumerated on the docs page."
                ),
            },
            "url": {"type": "string", "format": "uri"},
            "error": {"$ref": "#/components/schemas/Error"},
        },
        "required": ["id", "status"],
        "additionalProperties": True,
    }

    compat_spec = {
        "openapi": openai_spec.get("openapi", "3.1.0"),
        "info": {
            "title": "Gemini OpenAI-Compatible API",
            "version": "v1beta/openai",
            "description": (
                "Generated compatibility spec based on the upstream OpenAI spec, "
                "filtered to the subset Google currently documents for Gemini, with "
                "Gemini-only compatibility deltas added explicitly."
            ),
        },
        "servers": [
            {
                "url": "https://generativelanguage.googleapis.com/v1beta/openai",
                "description": "Gemini OpenAI-compatible API",
            }
        ],
        "security": [{"BearerAuth": []}],
        "paths": dict(sorted(paths.items())),
        "components": components,
    }

    if "/chat/completions" in compat_spec["paths"]:
        compat_spec["paths"]["/chat/completions"]["post"][
            "x-gemini-sdk-extra-body-schema"
        ] = _gemini_extra_body_ref("GeminiChatExtraBody")
        compat_spec["paths"]["/chat/completions"]["post"][
            "x-gemini-sdk-extra-body-note"
        ] = (
            "Google documents Gemini-specific compatibility fields through the "
            "OpenAI SDK `extra_body` passthrough. The raw REST wire shape is not "
            "shown on the docs page, so this schema is attached as a vendor "
            "extension instead of being merged into the upstream OpenAI request body."
        )

    if "/images/generations" in compat_spec["paths"]:
        compat_spec["paths"]["/images/generations"]["post"][
            "x-gemini-sdk-extra-body-schema"
        ] = _gemini_extra_body_ref("GeminiImagesExtraBody")

    compat_spec["paths"]["/videos"]["post"]["x-gemini-sdk-extra-body-schema"] = _gemini_extra_body_ref(
        "GeminiVideosExtraBody"
    )
    compat_spec["paths"]["/videos"]["post"]["responses"] = {
        "200": {
            "description": "Long-running video generation operation",
            "content": {
                "application/json": {
                    "schema": _gemini_extra_body_ref("GeminiVideoOperation")
                }
            },
        }
    }
    compat_spec["paths"]["/videos/{video_id}"]["get"]["responses"] = {
        "200": {
            "description": "Video generation operation status",
            "content": {
                "application/json": {
                    "schema": _gemini_extra_body_ref("GeminiVideoOperation")
                }
            },
        }
    }

    # Prune unreachable schemas from upstream OpenAI spec
    schema_count_before = len(compat_spec.get("components", {}).get("schemas", {}))
    pruned_count = _prune_unreachable_schemas(compat_spec)
    schema_count_after = len(compat_spec.get("components", {}).get("schemas", {}))

    upstream_operation_keys = {
        canonical_operation_key(method, path)
        for path, path_item in openai_spec.get("paths", {}).items()
        for method in path_item
        if method in {"get", "post", "patch", "delete"}
    }
    documented_operation_keys = {
        f"{item['method']} {item['path']}"
        for item in compat_surface["explicit_rest_operations"]
    } | {
        f"{item['method']} {item['path']}"
        for item in compat_surface["sdk_inferred_operations"]
    }
    gemini_only_operation_keys = {
        "POST /videos",
        "GET /videos/{video_id}",
    }
    covered_or_documented_keys = (
        set(copied_from_upstream) | set(missing_from_upstream) | gemini_only_operation_keys
    )

    report = {
        "upstream_operation_count": sum(
            1
            for path_item in openai_spec.get("paths", {}).values()
            for method in path_item
            if method in {"get", "post", "patch", "delete"}
        ),
        "google_documented_operation_count": len(documented_operation_keys),
        "copied_from_upstream": copied_from_upstream,
        "missing_from_upstream": sorted(set(missing_from_upstream)),
        "upstream_only_paths": sorted(upstream_operation_keys - covered_or_documented_keys),
        "gemini_only_paths": [
            "POST /videos",
            "GET /videos/{video_id}",
        ],
        "gemini_sdk_extra_body_operations": [
            "POST /chat/completions",
            "POST /images/generations",
            "POST /videos",
        ],
        "schema_count_before_pruning": schema_count_before,
        "schema_count_after_pruning": schema_count_after,
        "schemas_pruned": pruned_count,
    }
    return compat_spec, report


def main() -> None:
    spec, report = build_spec()
    write_json(OPENAPI_DIR / "gemini-openai-compat.openapi.json", spec)
    write_json(REPORTS_DIR / "openai-compat-diff-report.json", report)
    print(f"Saved OpenAI compatibility spec to {OPENAPI_DIR / 'gemini-openai-compat.openapi.json'}")


if __name__ == "__main__":
    main()
