#!/usr/bin/env python3

from __future__ import annotations

from collections import Counter

from _gemini_common import (
    OPENAPI_DIR,
    REPORTS_DIR,
    canonical_operation_key,
    read_json,
    write_json,
)


def _classify_upstream_only_operation(operation_key: str) -> dict[str, str]:
    method, path = operation_key.split(" ", 1)
    first_segment = next((segment for segment in path.split("/") if segment), "")

    documented_subset_families = {"chat", "images", "models", "batches"}
    if first_segment in documented_subset_families:
        subset_classification = "likely_intentionally_unsupported_subset_gap"
        subset_reason = (
            "Google documents this OpenAI-compatible family, but not this upstream "
            "operation."
        )
        if (
            operation_key == "GET /batches"
            or operation_key == "POST /batches/{batch_id}/cancel"
        ):
            subset_classification = "sdk_adjacent_undocumented_subset_gap"
            subset_reason = (
                "Google documents batch create and retrieve through SDK examples, so this "
                "adjacent batch-management operation is plausible but still undocumented."
            )
        return {
            "classification": "documented_family_subset_gap",
            "subset_classification": subset_classification,
            "family": first_segment,
            "reason": subset_reason,
        }

    family_map = {
        "organization": (
            "openai_admin_surface",
            "organization",
            "OpenAI organization and admin APIs are outside Google's documented Gemini compatibility surface.",
        ),
        "assistants": (
            "openai_assistants_surface",
            "assistants",
            "Assistants API endpoints are outside Google's documented Gemini compatibility surface.",
        ),
        "threads": (
            "openai_assistants_surface",
            "threads",
            "Threads and Runs endpoints are outside Google's documented Gemini compatibility surface.",
        ),
        "vector_stores": (
            "openai_assistants_surface",
            "vector_stores",
            "Vector store endpoints are outside Google's documented Gemini compatibility surface.",
        ),
        "responses": (
            "openai_responses_surface",
            "responses",
            "Responses API endpoints are outside Google's documented Gemini compatibility surface.",
        ),
        "evals": (
            "openai_evals_surface",
            "evals",
            "Evals endpoints are outside Google's documented Gemini compatibility surface.",
        ),
        "fine_tuning": (
            "openai_fine_tuning_surface",
            "fine_tuning",
            "Fine-tuning endpoints are outside Google's documented Gemini compatibility surface.",
        ),
        "files": (
            "openai_files_uploads_surface",
            "files",
            "OpenAI file-management endpoints are outside Google's documented Gemini compatibility surface.",
        ),
        "uploads": (
            "openai_files_uploads_surface",
            "uploads",
            "OpenAI multipart upload endpoints are outside Google's documented Gemini compatibility surface.",
        ),
        "audio": (
            "openai_audio_surface",
            "audio",
            "Audio speech and transcription endpoints are outside Google's documented Gemini compatibility surface.",
        ),
        "realtime": (
            "openai_realtime_surface",
            "realtime",
            "Realtime endpoints are outside Google's documented Gemini compatibility surface.",
        ),
        "completions": (
            "legacy_openai_generation_surface",
            "completions",
            "Legacy completions endpoints are outside Google's documented Gemini compatibility surface.",
        ),
        "moderations": (
            "legacy_openai_generation_surface",
            "moderations",
            "Moderations endpoints are outside Google's documented Gemini compatibility surface.",
        ),
    }
    classification, family, reason = family_map.get(
        first_segment,
        (
            "unclassified_upstream_only",
            first_segment or "root",
            "This upstream OpenAI operation is not part of Google's currently documented Gemini compatibility surface.",
        ),
    )
    return {
        "classification": classification,
        "subset_classification": "not_applicable",
        "family": family,
        "reason": reason,
    }


def main() -> None:
    compat_surface = read_json(REPORTS_DIR / "openai-compat-surface.json")
    compat_spec = read_json(OPENAPI_DIR / "gemini-openai-compat.openapi.json")
    diff_report = read_json(REPORTS_DIR / "openai-compat-diff-report.json")

    required_keys = {
        canonical_operation_key(item["method"], item["path"])
        for item in compat_surface["explicit_rest_operations"]
    }
    required_keys.update(
        canonical_operation_key(item["method"], item["path"])
        for item in compat_surface["sdk_inferred_operations"]
    )
    spec_keys = {
        canonical_operation_key(method, path)
        for path, path_item in compat_spec["paths"].items()
        for method in path_item
        if method in {"get", "post", "patch", "delete"}
    }

    missing = sorted(required_keys - spec_keys)
    compat_generic_operations: list[str] = []
    extension_schema_expectations = {
        "POST /chat/completions": "GeminiChatExtraBody",
        "POST /images/generations": "GeminiImagesExtraBody",
        "POST /videos": "GeminiVideosExtraBody",
    }
    invalid_extension_schemas: list[dict[str, str | None]] = []
    missing_video_operation_bindings: list[str] = []

    for path, path_item in compat_spec["paths"].items():
        for method, operation in path_item.items():
            if method not in {"get", "post", "patch", "delete"}:
                continue
            request_schemas = [
                content.get("schema")
                for content in operation.get("requestBody", {}).get("content", {}).values()
            ]
            response_schemas = [
                content.get("schema")
                for response in operation.get("responses", {}).values()
                for content in response.get("content", {}).values()
            ]
            if any(
                schema == {"$ref": "#/components/schemas/GenericJsonObject"}
                for schema in [*request_schemas, *response_schemas]
            ):
                compat_generic_operations.append(
                    canonical_operation_key(method, path)
                )

    for operation_key, expected_schema_name in extension_schema_expectations.items():
        method, path = operation_key.split(" ", 1)
        operation = compat_spec["paths"].get(path, {}).get(method.lower())
        actual_ref = None
        if operation is not None:
            actual_ref = (
                operation.get("x-gemini-sdk-extra-body-schema", {}).get("$ref")
            )
        expected_ref = f"#/components/schemas/{expected_schema_name}"
        if actual_ref != expected_ref:
            invalid_extension_schemas.append(
                {
                    "operation": operation_key,
                    "expected": expected_ref,
                    "actual": actual_ref,
                }
            )

    for operation_key in ["POST /videos", "GET /videos/{video_id}"]:
        method, path = operation_key.split(" ", 1)
        operation = compat_spec["paths"].get(path, {}).get(method.lower(), {})
        response_schema_ref = (
            operation.get("responses", {})
            .get("200", {})
            .get("content", {})
            .get("application/json", {})
            .get("schema", {})
            .get("$ref")
        )
        if response_schema_ref != "#/components/schemas/GeminiVideoOperation":
            missing_video_operation_bindings.append(operation_key)

    upstream_only_classifications = [
        {
            "operation": operation_key,
            **_classify_upstream_only_operation(operation_key),
        }
        for operation_key in diff_report["upstream_only_paths"]
    ]
    upstream_only_classification_counts = dict(
        sorted(
            Counter(
                item["classification"] for item in upstream_only_classifications
            ).items()
        )
    )
    upstream_only_subset_classification_counts = dict(
        sorted(
            Counter(
                item["subset_classification"] for item in upstream_only_classifications
            ).items()
        )
    )
    upstream_only_family_counts = dict(
        sorted(Counter(item["family"] for item in upstream_only_classifications).items())
    )
    compat_watchlist = [
        {
            "operation": item["operation"],
            "reason": item["reason"],
            "watch_reason": (
                "Batch create and retrieve are already present in Google's compatibility "
                "story, so this adjacent operation is worth rechecking against future docs."
            ),
        }
        for item in upstream_only_classifications
        if item["subset_classification"] == "sdk_adjacent_undocumented_subset_gap"
    ]

    report = {
        "required_operation_count": len(required_keys),
        "spec_operation_count": len(spec_keys),
        "compat_generic_operation_count": len(compat_generic_operations),
        "compat_generic_operations": compat_generic_operations,
        "missing_required_operations": missing,
        "invalid_extension_schemas": invalid_extension_schemas,
        "missing_video_operation_bindings": missing_video_operation_bindings,
        "upstream_operation_count": diff_report["upstream_operation_count"],
        "google_documented_operation_count": diff_report["google_documented_operation_count"],
        "gemini_only_paths": diff_report["gemini_only_paths"],
        "missing_from_upstream": diff_report["missing_from_upstream"],
        "upstream_only_paths": diff_report["upstream_only_paths"],
        "upstream_only_classification_counts": upstream_only_classification_counts,
        "upstream_only_subset_classification_counts": (
            upstream_only_subset_classification_counts
        ),
        "upstream_only_family_counts": upstream_only_family_counts,
        "upstream_only_classifications": upstream_only_classifications,
        "compat_watchlist": compat_watchlist,
    }
    write_json(REPORTS_DIR / "openai-compat-validation-report.json", report)

    if missing:
        print("Missing required OpenAI-compatible operations:")
        for item in missing:
            print(f"  {item}")
        raise SystemExit(1)

    if invalid_extension_schemas:
        print("Invalid Gemini compatibility extension schema bindings:")
        for item in invalid_extension_schemas:
            print(
                f"  {item['operation']}: expected {item['expected']}, got {item['actual']}"
            )
        raise SystemExit(1)

    if compat_generic_operations:
        print("Compat spec still contains generic placeholder operations:")
        for item in compat_generic_operations:
            print(f"  {item}")
        raise SystemExit(1)

    if missing_video_operation_bindings:
        print("Compat video operations are missing GeminiVideoOperation responses:")
        for item in missing_video_operation_bindings:
            print(f"  {item}")
        raise SystemExit(1)

    print("OpenAI compatibility validation passed")


if __name__ == "__main__":
    main()
