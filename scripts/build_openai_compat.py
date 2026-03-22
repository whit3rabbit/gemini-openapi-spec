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
    }
    return compat_spec, report


def main() -> None:
    spec, report = build_spec()
    write_json(OPENAPI_DIR / "gemini-openai-compat.openapi.json", spec)
    write_json(REPORTS_DIR / "openai-compat-diff-report.json", report)
    print(f"Saved OpenAI compatibility spec to {OPENAPI_DIR / 'gemini-openai-compat.openapi.json'}")


if __name__ == "__main__":
    main()
