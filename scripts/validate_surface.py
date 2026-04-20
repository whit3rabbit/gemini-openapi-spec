#!/usr/bin/env python3

from __future__ import annotations

from _gemini_common import (
    OPENAPI_DIR,
    REPORTS_DIR,
    canonical_operation_key,
    load_batch_guide_evidence,
    load_doc_operations,
    load_file_search_stores_reference_evidence,
    load_files_guide_evidence,
    load_generate_content_reference_evidence,
    read_json,
    write_json,
)
from native_schema_registry import selected_native_operation_keys


def main() -> None:
    doc_operations = load_doc_operations()
    batch_guide_evidence = load_batch_guide_evidence()
    file_search_stores_reference_evidence = load_file_search_stores_reference_evidence()
    files_guide_evidence = load_files_guide_evidence()
    generate_content_reference_evidence = load_generate_content_reference_evidence()
    spec = read_json(OPENAPI_DIR / "gemini-native.openapi.json")

    doc_keys = {
        canonical_operation_key(operation.method, operation.normalized_path)
        for operation in doc_operations
    }
    spec_keys = {
        canonical_operation_key(method, path)
        for path, path_item in spec["paths"].items()
        for method in path_item
        if method in {"get", "post", "patch", "delete"}
    }

    missing_from_spec = sorted(doc_keys - spec_keys)
    undocumented_in_docs = sorted(spec_keys - doc_keys)
    documented_alias_paths = {
        canonical_operation_key("post", item["path"])
        for item in files_guide_evidence.get("documented_aliases", [])
    }
    documented_reference_alias_paths = {
        canonical_operation_key(item["method"], item["normalized_path"])
        for item in file_search_stores_reference_evidence.get("documented_aliases", [])
    }
    guide_documented_operation_keys = {
        canonical_operation_key(item["method"], item["normalized_path"])
        for item in batch_guide_evidence.get("documented_operations", [])
    }
    expected_guide_documented_keys = documented_alias_paths | guide_documented_operation_keys
    guide_documented_missing_from_native_spec = sorted(
        expected_guide_documented_keys - spec_keys
    )
    documented_guide_only_aliases = [
        {
            "operation": item,
            "reason": (
                "The official Gemini Files guide documents this upload alias, but the "
                "all-methods index does not list it as a standalone operation."
            ),
            "docs_sources": [files_guide_evidence["source"]],
            "guide_evidence": next(
                (
                    alias.get("evidence")
                    for alias in files_guide_evidence.get("documented_aliases", [])
                    if canonical_operation_key("post", alias["path"]) == item
                ),
                None,
            ),
        }
        for item in undocumented_in_docs
        if item in documented_alias_paths
    ]
    documented_guide_only_operations = [
        {
            "operation": item,
            "reason": (
                "This operation is documented in an official Gemini guide, but it does not "
                "appear in the all-methods index."
            ),
            "docs_sources": [batch_guide_evidence["source"]],
            "guide_evidence": next(
                (
                    guide_operation.get("evidence")
                    for guide_operation in batch_guide_evidence.get("documented_operations", [])
                    if canonical_operation_key(
                        guide_operation["method"], guide_operation["normalized_path"]
                    )
                    == item
                ),
                None,
            ),
        }
        for item in undocumented_in_docs
        if item in guide_documented_operation_keys
    ]
    documented_reference_only_aliases = [
        {
            "operation": item,
            "reason": (
                "This upload alias is documented in the official File Search Stores "
                "reference, but it does not appear in the all-methods index."
            ),
            "docs_sources": [file_search_stores_reference_evidence["source"]],
            "guide_evidence": next(
                (
                    alias.get("evidence")
                    for alias in file_search_stores_reference_evidence.get(
                        "documented_aliases", []
                    )
                    if canonical_operation_key(
                        alias["method"], alias["normalized_path"]
                    )
                    == item
                ),
                None,
            ),
        }
        for item in undocumented_in_docs
        if item in documented_reference_alias_paths
    ]
    undocumented_in_docs_unclassified = [
        item
        for item in undocumented_in_docs
        if item not in documented_alias_paths
        and item not in guide_documented_operation_keys
        and item not in documented_reference_alias_paths
    ]
    native_generic_operations = []
    selected_keys = selected_native_operation_keys()
    unconcretized_selected_operations = []
    invalid_guide_backed_operations = []
    invalid_streaming_operations = []

    for path, path_item in spec["paths"].items():
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
                native_generic_operations.append(
                    canonical_operation_key(method, path)
                )

    for method, path in selected_keys:
        operation = spec["paths"].get(path, {}).get(method.lower())
        if not operation:
            unconcretized_selected_operations.append(f"{method} {path} (missing)")
            continue
        request_schema = (
            operation.get("requestBody", {})
            .get("content", {})
            .get("application/json", {})
            .get("schema")
        )
        response_schemas = [
            content.get("schema")
            for content in (
                operation.get("responses", {}).get("200", {}).get("content", {}).values()
            )
        ]
        for schema in (request_schema, *response_schemas):
            if schema == {"$ref": "#/components/schemas/GenericJsonObject"}:
                unconcretized_selected_operations.append(f"{method} {path}")
                break

    batch_download_operation = spec["paths"].get("/download/v1beta/files/{file}:download", {}).get(
        "get"
    )
    files_upload_alias_operation = spec["paths"].get("/upload/v1beta/files", {}).get("post")
    if batch_download_operation:
        alt_parameter = next(
            (
                parameter
                for parameter in batch_download_operation.get("parameters", [])
                if parameter.get("name") == "alt" and parameter.get("in") == "query"
            ),
            None,
        )
        binary_response = (
            batch_download_operation.get("responses", {})
            .get("200", {})
            .get("content", {})
            .get("application/octet-stream", {})
            .get("schema")
        )
        if not alt_parameter or alt_parameter.get("required") is not True:
            invalid_guide_backed_operations.append(
                "GET /download/v1beta/files/{file}:download (missing required alt query parameter)"
            )
        elif alt_parameter.get("schema", {}).get("enum") != ["media"]:
            invalid_guide_backed_operations.append(
                "GET /download/v1beta/files/{file}:download (alt query parameter is not constrained to media)"
            )
        if binary_response != {"type": "string", "format": "binary"}:
            invalid_guide_backed_operations.append(
                "GET /download/v1beta/files/{file}:download (missing binary media response)"
            )
    if files_upload_alias_operation:
        upload_binary_request = (
            files_upload_alias_operation.get("requestBody", {})
            .get("content", {})
            .get("application/octet-stream", {})
            .get("schema")
        )
        if upload_binary_request != {"type": "string", "format": "binary"}:
            invalid_guide_backed_operations.append(
                "POST /upload/v1beta/files (missing binary upload request body)"
            )

    stream_generate_content_operation = spec["paths"].get(
        "/v1beta/models/{model}:streamGenerateContent", {}
    ).get("post")
    if stream_generate_content_operation:
        request_schema = (
            stream_generate_content_operation.get("requestBody", {})
            .get("content", {})
            .get("application/json", {})
            .get("schema")
        )
        alt_parameter = next(
            (
                parameter
                for parameter in stream_generate_content_operation.get("parameters", [])
                if parameter.get("name") == "alt" and parameter.get("in") == "query"
            ),
            None,
        )
        event_stream_schema = (
            stream_generate_content_operation.get("responses", {})
            .get("200", {})
            .get("content", {})
            .get("text/event-stream", {})
            .get("schema")
        )
        event_stream_ref = stream_generate_content_operation.get(
            "x-gemini-stream-event-schema"
        )
        if request_schema != {"$ref": "#/components/schemas/GenerateContentRequest"}:
            invalid_streaming_operations.append(
                "POST /v1beta/models/{model}:streamGenerateContent (request body is not GenerateContentRequest)"
            )
        if not alt_parameter or alt_parameter.get("required") is not True:
            invalid_streaming_operations.append(
                "POST /v1beta/models/{model}:streamGenerateContent (missing required alt query parameter)"
            )
        elif alt_parameter.get("schema", {}).get("enum") != ["sse"]:
            invalid_streaming_operations.append(
                "POST /v1beta/models/{model}:streamGenerateContent (alt query parameter is not constrained to sse)"
            )
        if event_stream_schema != {"type": "string"}:
            invalid_streaming_operations.append(
                "POST /v1beta/models/{model}:streamGenerateContent (missing text/event-stream response body)"
            )
        if event_stream_ref != {"$ref": "#/components/schemas/GenerateContentResponse"}:
            invalid_streaming_operations.append(
                "POST /v1beta/models/{model}:streamGenerateContent (missing GenerateContentResponse event schema hint)"
            )
        if not generate_content_reference_evidence.get("stream_generate_content", {}).get(
            "event_stream_response_evidence"
        ):
            invalid_streaming_operations.append(
                "POST /v1beta/models/{model}:streamGenerateContent (missing checked-in stream response evidence)"
            )
        if not generate_content_reference_evidence.get("stream_generate_content", {}).get(
            "alt_sse_evidence"
        ):
            invalid_streaming_operations.append(
                "POST /v1beta/models/{model}:streamGenerateContent (missing checked-in alt=sse evidence)"
            )

    # Coverage summary: count operations by source
    all_methods_covered = len(doc_keys & spec_keys)
    guide_covered = len(
        (documented_alias_paths | guide_documented_operation_keys | documented_reference_alias_paths)
        & spec_keys
    )
    all_source_keys = (
        doc_keys
        | documented_alias_paths
        | guide_documented_operation_keys
        | documented_reference_alias_paths
    )
    coverage_pct = (
        len(all_source_keys & spec_keys) / len(all_source_keys) * 100
        if all_source_keys
        else 0
    )

    report = {
        "doc_operation_count": len(doc_keys),
        "spec_operation_count": len(spec_keys),
        "native_generic_operation_count": len(native_generic_operations),
        "native_generic_operations": native_generic_operations,
        "missing_from_spec": missing_from_spec,
        "undocumented_in_docs": undocumented_in_docs,
        "undocumented_in_docs_unclassified": undocumented_in_docs_unclassified,
        "guide_documented_missing_from_native_spec": guide_documented_missing_from_native_spec,
        "documented_guide_only_aliases": documented_guide_only_aliases,
        "documented_guide_only_operations": documented_guide_only_operations,
        "documented_reference_only_aliases": documented_reference_only_aliases,
        "invalid_guide_backed_operations": invalid_guide_backed_operations,
        "invalid_streaming_operations": invalid_streaming_operations,
        "unconcretized_selected_operations": unconcretized_selected_operations,
        "coverage_summary": {
            "all_methods_operations": len(doc_keys),
            "all_methods_covered": all_methods_covered,
            "guide_operations": len(
                documented_alias_paths | guide_documented_operation_keys | documented_reference_alias_paths
            ),
            "guide_covered": guide_covered,
            "total_documented_operations": len(all_source_keys),
            "total_spec_operations": len(spec_keys),
            "coverage_percent": round(coverage_pct, 1),
        },
    }
    write_json(REPORTS_DIR / "validation-report.json", report)

    if missing_from_spec:
        print("Missing operations compared with live docs:")
        for item in missing_from_spec:
            print(f"  {item}")
        raise SystemExit(1)

    if unconcretized_selected_operations:
        print("Selected operations still use the generic placeholder schema:")
        for item in unconcretized_selected_operations:
            print(f"  {item}")
        raise SystemExit(1)

    if guide_documented_missing_from_native_spec:
        print("Guide-documented operations missing from native spec:")
        for item in guide_documented_missing_from_native_spec:
            print(f"  {item}")
        raise SystemExit(1)

    if invalid_guide_backed_operations:
        print("Guide-backed operations are present but malformed:")
        for item in invalid_guide_backed_operations:
            print(f"  {item}")
        raise SystemExit(1)

    if invalid_streaming_operations:
        print("Streaming operations are present but malformed:")
        for item in invalid_streaming_operations:
            print(f"  {item}")
        raise SystemExit(1)

    cs = report["coverage_summary"]
    print("Surface validation passed")
    print(
        f"Coverage: {cs['total_spec_operations']} spec operations, "
        f"{cs['total_documented_operations']} documented across all sources, "
        f"{cs['coverage_percent']}% documented coverage"
    )
    print(
        f"  all-methods: {cs['all_methods_covered']}/{cs['all_methods_operations']}, "
        f"guides: {cs['guide_covered']}/{cs['guide_operations']}"
    )
    if undocumented_in_docs_unclassified:
        print("Spec has extra operations not present in current docs:")
        for item in undocumented_in_docs_unclassified:
            print(f"  {item}")
    if documented_guide_only_aliases:
        print("Spec has guide-documented aliases not listed in the all-methods index:")
        for item in documented_guide_only_aliases:
            print(f"  {item['operation']}")
    if documented_guide_only_operations:
        print("Spec has guide-documented operations not listed in the all-methods index:")
        for item in documented_guide_only_operations:
            print(f"  {item['operation']}")
    if documented_reference_only_aliases:
        print("Spec has reference-documented aliases not listed in the all-methods index:")
        for item in documented_reference_only_aliases:
            print(f"  {item['operation']}")


if __name__ == "__main__":
    main()
