#!/usr/bin/env python3

from __future__ import annotations

from datetime import datetime, timezone

from _gemini_common import (
    DISCOVERY_DIR,
    OPENAPI_DIR,
    REPORTS_DIR,
    canonical_operation_key,
    load_batch_guide_evidence,
    load_doc_operations,
    load_files_guide_evidence,
    load_tuning_reference_evidence,
    load_tuning_permissions_reference_evidence,
    read_json,
    write_json,
)


def _write_markdown_summary(
    report: dict,
    validation_report: dict,
    compat_validation: dict,
) -> None:
    compat_watchlist = compat_validation.get("compat_watchlist", [])
    lines = [
        "# Drift Summary",
        "",
        f"Generated: {report['generated_at_utc']}",
        "",
        "## Native",
        f"- Native generic operations: {validation_report['native_generic_operation_count']}",
        f"- Live docs operations: {validation_report['doc_operation_count']}",
        f"- Native spec operations: {validation_report['spec_operation_count']}",
        f"- Guide-only aliases: {len(validation_report['documented_guide_only_aliases'])}",
        f"- Guide-only operations: {len(validation_report['documented_guide_only_operations'])}",
        f"- Reference-only aliases: {len(validation_report['documented_reference_only_aliases'])}",
        "",
        "## Docs vs Discovery",
        (
            "- Missing from discovery after version normalization: "
            f"{len(report['docs_vs_discovery']['missing_from_discovery_after_version_normalization'])}"
        ),
        (
            "- Extra in discovery after version normalization: "
            f"{len(report['docs_vs_discovery']['extra_in_discovery_after_version_normalization'])}"
        ),
        "",
        "## SDK vs Native",
        (
            "- High-confidence SDK paths missing from docs: "
            f"{len(report['sdk_vs_native']['paths_missing_from_docs'])}"
        ),
        (
            "- High-confidence SDK paths missing from native spec: "
            f"{len(report['sdk_vs_native']['paths_missing_from_native_spec'])}"
        ),
        "",
        "## Compat",
        f"- Compat generic operations: {compat_validation['compat_generic_operation_count']}",
        (
            "- Google-documented compat operations: "
            f"{compat_validation['google_documented_operation_count']}"
        ),
        (
            "- Upstream OpenAI operations: "
            f"{compat_validation['upstream_operation_count']}"
        ),
        (
            "- Gemini-only compat paths: "
            f"{len(compat_validation['gemini_only_paths'])}"
        ),
        (
            "- Upstream-only compat paths: "
            f"{len(compat_validation['upstream_only_paths'])}"
        ),
        (
            "- Upstream-only classification counts: "
            f"{compat_validation['upstream_only_classification_counts']}"
        ),
        (
            "- Upstream-only subset counts: "
            f"{compat_validation['upstream_only_subset_classification_counts']}"
        ),
        "",
        "## Compat Watchlist",
    ]
    if compat_watchlist:
        lines.extend(
            f"- {item['operation']}: {item['watch_reason']}" for item in compat_watchlist
        )
    else:
        lines.append("- None")

    (REPORTS_DIR / "drift-summary.md").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def _write_json_summary(
    report: dict,
    validation_report: dict,
    compat_validation: dict,
) -> None:
    payload = {
        "generated_at_utc": report["generated_at_utc"],
        "native": {
            "generic_operation_count": validation_report["native_generic_operation_count"],
            "doc_operation_count": validation_report["doc_operation_count"],
            "spec_operation_count": validation_report["spec_operation_count"],
            "guide_only_alias_count": len(validation_report["documented_guide_only_aliases"]),
            "guide_only_operation_count": len(
                validation_report["documented_guide_only_operations"]
            ),
            "reference_only_alias_count": len(
                validation_report["documented_reference_only_aliases"]
            ),
        },
        "docs_vs_discovery": {
            "missing_from_discovery_after_version_normalization_count": len(
                report["docs_vs_discovery"][
                    "missing_from_discovery_after_version_normalization"
                ]
            ),
            "extra_in_discovery_after_version_normalization_count": len(
                report["docs_vs_discovery"][
                    "extra_in_discovery_after_version_normalization"
                ]
            ),
        },
        "sdk_vs_native": {
            "paths_missing_from_docs_count": len(
                report["sdk_vs_native"]["paths_missing_from_docs"]
            ),
            "paths_missing_from_native_spec_count": len(
                report["sdk_vs_native"]["paths_missing_from_native_spec"]
            ),
        },
        "compat": {
            "generic_operation_count": compat_validation["compat_generic_operation_count"],
            "google_documented_operation_count": compat_validation[
                "google_documented_operation_count"
            ],
            "upstream_operation_count": compat_validation["upstream_operation_count"],
            "gemini_only_path_count": len(compat_validation["gemini_only_paths"]),
            "upstream_only_path_count": len(compat_validation["upstream_only_paths"]),
            "upstream_only_classification_counts": compat_validation[
                "upstream_only_classification_counts"
            ],
            "upstream_only_subset_classification_counts": compat_validation[
                "upstream_only_subset_classification_counts"
            ],
        },
        "compat_watchlist": compat_validation.get("compat_watchlist", []),
    }
    write_json(REPORTS_DIR / "drift-summary.json", payload)


def _write_compat_watchlist_markdown(compat_validation: dict) -> None:
    lines = [
        "# Compat Watchlist",
        "",
        "Undocumented batch-adjacent OpenAI-compatible operations worth rechecking against future Google docs.",
        "",
    ]
    watchlist = compat_validation.get("compat_watchlist", [])
    if watchlist:
        lines.extend(
            f"- {item['operation']}: {item['watch_reason']}" for item in watchlist
        )
    else:
        lines.append("- None")
    (REPORTS_DIR / "compat-watchlist.md").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def _normalize_discovery_path(path: str) -> str:
    if path.startswith("/v1beta3/"):
        return "/v1beta/" + path[len("/v1beta3/") :]
    if path == "/v1beta3":
        return "/v1beta"
    return path


def _sdk_candidate_path(module_name: str, fragment: str) -> tuple[str | None, str]:
    if fragment == "test/path":
        return None, "test-only fragment"

    if module_name == "batches.py":
        if fragment.startswith("batchPredictionJobs"):
            return None, "vertex-only batchPredictionJobs surface"
        if fragment == "batches":
            return "/v1beta/batches", "high"
        if fragment == "batches/{name}":
            return "/v1beta/batches/{batch}", "high"
        if fragment == "batches/{name}:cancel":
            return "/v1beta/batches/{batch}:cancel", "high"
        if fragment in {"{model}:asyncBatchEmbedContent", "{model}:batchGenerateContent"}:
            return f"/v1beta/models/{{model}}{fragment[len('{model}'):]}", "high"
        return f"/v1beta/{fragment}", "medium"

    if module_name == "caches.py":
        if fragment == "cachedContents":
            return "/v1beta/cachedContents", "high"
        if fragment == "{name}":
            return "/v1beta/cachedContents/{cachedContent}", "high"

    if module_name == "files.py":
        if fragment == "upload/v1beta/files":
            return "/upload/v1beta/files", "high"
        if fragment == "files/{name}:download":
            return "/v1beta/files/{file}:download", "high"
        return f"/v1beta/{fragment}", "high"

    if module_name == "models.py":
        if fragment == "{models_url}":
            return "/v1beta/models", "high"
        if fragment == "{model}" or fragment == "{name}":
            return "/v1beta/models/{model}", "high"
        if fragment.startswith("{model}:"):
            operation_suffix = fragment[len("{model}") :].split("?", 1)[0]
            return f"/v1beta/models/{{model}}{operation_suffix}", "high"
        return f"/v1beta/{fragment}", "medium"

    if module_name == "file_search_stores.py":
        if fragment == "fileSearchStores":
            return "/v1beta/fileSearchStores", "high"
        if fragment == "{file_search_store_name}:importFile":
            return "/v1beta/fileSearchStores/{fileSearchStore}:importFile", "high"
        if fragment == "{name}":
            return "/v1beta/fileSearchStores/{fileSearchStore}", "high"
        if fragment == "upload/v1beta/{file_search_store_name}:uploadToFileSearchStore":
            return "/v1beta/fileSearchStores/{fileSearchStore}:uploadToFileSearchStore", "medium"
        return f"/v1beta/{fragment}", "medium"

    if module_name == "documents.py":
        if fragment == "{parent}/documents":
            return None, "ambiguous parent placeholder"
        if fragment == "{name}":
            return None, "ambiguous document placeholder"

    if module_name == "operations.py":
        return None, "vertex-only operations surface"

    if module_name == "tunings.py":
        if fragment == "tuningJobs":
            return None, "vertex-only tuningJobs surface"
        if fragment == "tunedModels":
            return "/v1beta/tunedModels", "medium"
        if fragment == "{name}":
            return "/v1beta/tunedModels/{tunedModel}", "medium"
        if fragment == "{name}:cancel":
            return None, "no documented Gemini Developer cancel route for tunedModels"
        return None, "ambiguous tuning placeholder"

    if module_name == "tokens.py":
        return f"/v1beta/{fragment}", "medium"

    return None, "unmapped module"


def main() -> None:
    generated_at = datetime.now(timezone.utc).isoformat()
    doc_operations = load_doc_operations()
    batch_guide_evidence = load_batch_guide_evidence()
    files_guide_evidence = load_files_guide_evidence()
    discovery = read_json(DISCOVERY_DIR / "openapi3_0.json")
    sdk_surface = read_json(REPORTS_DIR / "python-genai-surface.json")
    native_spec = read_json(OPENAPI_DIR / "gemini-native.openapi.json")
    validation_report = read_json(REPORTS_DIR / "validation-report.json")
    compat_diff = read_json(REPORTS_DIR / "openai-compat-diff-report.json")
    compat_validation = read_json(REPORTS_DIR / "openai-compat-validation-report.json")

    tuning_evidence = load_tuning_reference_evidence()
    tuning_permissions_evidence = load_tuning_permissions_reference_evidence()

    doc_operation_keys = {
        canonical_operation_key(operation.method, operation.normalized_path)
        for operation in doc_operations
    }
    # Include tuning reference operations alongside all-methods
    tuning_operation_keys = {
        canonical_operation_key(item["method"], item["normalized_path"])
        for item in tuning_evidence.get("operations", [])
    } | {
        canonical_operation_key(item["method"], item["normalized_path"])
        for item in tuning_permissions_evidence.get("operations", [])
    }
    all_documented_operation_keys = doc_operation_keys | tuning_operation_keys
    doc_paths = sorted({operation.normalized_path for operation in doc_operations})

    discovery_exact_operation_keys: set[str] = set()
    discovery_version_normalized_operation_keys: set[str] = set()
    for path, path_item in discovery.get("paths", {}).items():
        normalized_path = _normalize_discovery_path(path)
        for method in ("get", "post", "patch", "delete"):
            if method in path_item:
                discovery_exact_operation_keys.add(canonical_operation_key(method, path))
                discovery_version_normalized_operation_keys.add(
                    canonical_operation_key(method, normalized_path)
                )

    native_spec_paths = sorted(native_spec["paths"])
    sdk_high_confidence_paths: set[str] = set()
    sdk_medium_confidence_paths: set[str] = set()
    sdk_skipped_fragments: list[dict[str, str]] = []

    module_path_records = sdk_surface.get("module_path_records")
    if module_path_records:
        record_iterable = [
            (
                module_name,
                record["path_fragment"],
                record.get("classification")
                or (
                    "developer_api_only"
                    if record.get("branch") == "developer_api"
                    else "vertexai_only"
                    if record.get("branch") == "vertexai"
                    else "shared_helper"
                ),
            )
            for module_name, records in module_path_records.items()
            for record in records
        ]
    else:
        record_iterable = [
            (module_name, fragment, "shared_helper")
            for module_name, fragments in sdk_surface["module_path_fragments"].items()
            for fragment in fragments
        ]

    seen_sdk_records: set[tuple[str, str, str]] = set()
    for module_name, fragment, classification in record_iterable:
        record_key = (module_name, str(fragment), str(classification))
        if record_key in seen_sdk_records:
            continue
        seen_sdk_records.add(record_key)

        if classification == "vertexai_only":
            sdk_skipped_fragments.append(
                {
                    "module": module_name,
                    "fragment": str(fragment),
                    "reason": "vertexai-only branch",
                }
            )
            continue

        candidate_path, confidence = _sdk_candidate_path(module_name, str(fragment))
        if classification == "shared_helper" and confidence == "medium":
            confidence = "high"

        for query_suffix in ("?alt=sse",):
            if candidate_path and candidate_path.endswith(query_suffix):
                candidate_path = candidate_path[: -len(query_suffix)]

        if candidate_path is None:
            sdk_skipped_fragments.append(
                {
                    "module": module_name,
                    "fragment": str(fragment),
                    "reason": confidence,
                }
            )
            continue
        if confidence == "high":
            sdk_high_confidence_paths.add(candidate_path)
        else:
            sdk_medium_confidence_paths.add(candidate_path)

    paths_missing_from_docs = sorted(set(sdk_high_confidence_paths) - set(doc_paths))
    paths_missing_from_native_spec = sorted(
        set(sdk_high_confidence_paths) - set(native_spec_paths)
    )
    guide_documented_operation_keys = {
        canonical_operation_key("post", item["path"])
        for item in files_guide_evidence.get("documented_aliases", [])
    } | {
        canonical_operation_key(item["method"], item["normalized_path"])
        for item in batch_guide_evidence.get("documented_operations", [])
    }
    documented_guide_alias_paths = {
        item["path"] for item in files_guide_evidence.get("documented_aliases", [])
    }
    download_policy = files_guide_evidence.get("download_policy", {})
    intentional_docs_first_exclusions = [
        {
            "path": path,
            "reason": (
                "The python-genai Gemini Developer client exposes this route, but the official "
                "Gemini Files guide says uploaded files cannot be downloaded."
            ),
            "docs_sources": [files_guide_evidence["source"]],
            "guide_evidence": download_policy.get("evidence"),
        }
        for path in paths_missing_from_docs
        if path == "/v1beta/files/{file}:download"
        and download_policy.get("download_allowed") is False
    ]
    documented_guide_only_aliases = [
        {
            "path": path,
            "reason": (
                "This upload alias is documented in the official Gemini Files guide, but it "
                "does not appear as a standalone operation in the all-methods index."
            ),
            "docs_sources": [files_guide_evidence["source"]],
            "guide_evidence": next(
                (
                    item.get("evidence")
                    for item in files_guide_evidence.get("documented_aliases", [])
                    if item.get("path") == path
                ),
                None,
            ),
        }
        for path in paths_missing_from_docs
        if path in documented_guide_alias_paths
    ]
    excluded_paths = {
        item["path"] for item in intentional_docs_first_exclusions + documented_guide_only_aliases
    }

    report = {
        "generated_at_utc": generated_at,
        "docs_vs_discovery": {
            "doc_operation_count": len(doc_operation_keys),
            "discovery_exact_operation_count": len(discovery_exact_operation_keys),
            "discovery_version_normalized_operation_count": len(
                discovery_version_normalized_operation_keys
            ),
            "missing_from_discovery_after_version_normalization": sorted(
                all_documented_operation_keys - discovery_version_normalized_operation_keys
            ),
            "extra_in_discovery_after_version_normalization": sorted(
                discovery_version_normalized_operation_keys - all_documented_operation_keys
            ),
            "discovery_version": discovery["info"]["version"],
            "discovery_revision": discovery["info"].get("x-google-revision"),
        },
        "guides_vs_native": {
            "guide_documented_operations": sorted(guide_documented_operation_keys),
            "guide_documented_not_in_all_methods": sorted(
                guide_documented_operation_keys - doc_operation_keys
            ),
            "guide_documented_missing_from_native_spec": sorted(
                guide_documented_operation_keys - set(
                    canonical_operation_key(method, path)
                    for path, path_item in native_spec["paths"].items()
                    for method in path_item
                    if method in {"get", "post", "patch", "delete"}
                )
            ),
            "questionable_examples": batch_guide_evidence.get("questionable_examples", []),
        },
        "sdk_vs_native": {
            "developer_api_only_modules": sdk_surface.get(
                "developer_api_only_modules", []
            ),
            "high_confidence_path_count": len(sdk_high_confidence_paths),
            "medium_confidence_path_count": len(sdk_medium_confidence_paths),
            "mixed_surface_modules": sdk_surface.get("mixed_surface_modules", []),
            "mixed_with_shared_helper_modules": sdk_surface.get(
                "mixed_with_shared_helper_modules", []
            ),
            "paths_missing_from_docs": paths_missing_from_docs,
            "paths_missing_from_docs_unclassified": [
                path for path in paths_missing_from_docs if path not in excluded_paths
            ],
            "paths_missing_from_native_spec": paths_missing_from_native_spec,
            "paths_missing_from_native_spec_unclassified": [
                path
                for path in paths_missing_from_native_spec
                if path
                not in {item["path"] for item in intentional_docs_first_exclusions}
            ],
            "intentional_docs_first_exclusions": intentional_docs_first_exclusions,
            "documented_guide_only_aliases": documented_guide_only_aliases,
            "docs_paths_missing_from_sdk_high_confidence": sorted(
                set(doc_paths) - set(sdk_high_confidence_paths)
            ),
            "skipped_fragments": sorted(
                sdk_skipped_fragments,
                key=lambda item: (item["module"], item["fragment"]),
            ),
            "vertexai_only_modules": sdk_surface.get("vertexai_only_modules", []),
        },
        "compat_vs_upstream": {
            "upstream_operation_count": compat_diff["upstream_operation_count"],
            "google_documented_operation_count": compat_diff["google_documented_operation_count"],
            "copied_from_upstream": compat_diff["copied_from_upstream"],
            "gemini_only_paths": compat_diff["gemini_only_paths"],
            "gemini_sdk_extra_body_operations": compat_diff[
                "gemini_sdk_extra_body_operations"
            ],
            "missing_from_upstream": compat_diff["missing_from_upstream"],
            "upstream_only_paths": compat_diff["upstream_only_paths"],
            "compat_generic_operation_count": compat_validation[
                "compat_generic_operation_count"
            ],
            "upstream_only_classification_counts": compat_validation[
                "upstream_only_classification_counts"
            ],
            "upstream_only_subset_classification_counts": compat_validation[
                "upstream_only_subset_classification_counts"
            ],
            "upstream_only_family_counts": compat_validation[
                "upstream_only_family_counts"
            ],
            "compat_watchlist": compat_validation["compat_watchlist"],
        },
    }
    write_json(REPORTS_DIR / "source-drift-report.json", report)
    _write_markdown_summary(report, validation_report, compat_validation)
    _write_json_summary(report, validation_report, compat_validation)
    _write_compat_watchlist_markdown(compat_validation)
    print(f"Saved drift report to {REPORTS_DIR / 'source-drift-report.json'}")
    print(f"Saved markdown summary to {REPORTS_DIR / 'drift-summary.md'}")
    print(f"Saved json summary to {REPORTS_DIR / 'drift-summary.json'}")
    print(f"Saved compat watchlist to {REPORTS_DIR / 'compat-watchlist.md'}")


if __name__ == "__main__":
    main()
