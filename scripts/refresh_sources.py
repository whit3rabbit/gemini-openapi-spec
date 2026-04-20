#!/usr/bin/env python3

from __future__ import annotations

from _gemini_common import (
    ALL_METHODS_URL,
    BATCH_GUIDE_URL,
    DISCOVERY_URL,
    DISCOVERY_DIR,
    DOCS_DIR,
    GENERATE_CONTENT_REF_URL,
    FILE_SEARCH_DOCUMENTS_REF_URL,
    FILE_SEARCH_STORES_REF_URL,
    FILES_GUIDE_URL,
    MODELS_REF_URL,
    OPENAI_COMPAT_URL,
    OPENAI_DIR,
    OPENAI_UPSTREAM_SPEC_URL,
    TOKENS_REF_URL,
    ensure_dirs,
    fetch_json,
    fetch_text,
    parse_all_methods_html,
    parse_batch_guide_html,
    parse_file_search_documents_reference_html,
    parse_file_search_stores_reference_html,
    parse_files_guide_html,
    parse_generate_content_reference_html,
    parse_models_reference_html,
    parse_tokens_reference_html,
    write_json,
)


def main() -> None:
    ensure_dirs()

    discovery = fetch_json(DISCOVERY_URL)
    write_json(DISCOVERY_DIR / "openapi3_0.json", discovery)

    html = fetch_text(ALL_METHODS_URL)
    (DOCS_DIR / "all-methods.html").write_text(html, encoding="utf-8")

    operations = parse_all_methods_html(html)
    write_json(
        DOCS_DIR / "all-methods.json",
        {
            "source": ALL_METHODS_URL,
            "operation_count": len(operations),
            "operations": [operation.to_json() for operation in operations],
        },
    )

    files_guide_html = fetch_text(FILES_GUIDE_URL)
    (DOCS_DIR / "files-guide.html").write_text(files_guide_html, encoding="utf-8")
    write_json(DOCS_DIR / "files-guide.json", parse_files_guide_html(files_guide_html))

    batch_guide_html = fetch_text(BATCH_GUIDE_URL)
    (DOCS_DIR / "batch-guide.html").write_text(batch_guide_html, encoding="utf-8")
    write_json(DOCS_DIR / "batch-guide.json", parse_batch_guide_html(batch_guide_html))

    models_ref_html = fetch_text(MODELS_REF_URL)
    (DOCS_DIR / "models-reference.html").write_text(models_ref_html, encoding="utf-8")
    write_json(DOCS_DIR / "models-reference.json", parse_models_reference_html(models_ref_html))

    tokens_ref_html = fetch_text(TOKENS_REF_URL)
    (DOCS_DIR / "tokens-reference.html").write_text(tokens_ref_html, encoding="utf-8")
    write_json(DOCS_DIR / "tokens-reference.json", parse_tokens_reference_html(tokens_ref_html))

    generate_content_ref_html = fetch_text(GENERATE_CONTENT_REF_URL)
    (DOCS_DIR / "generate-content-reference.html").write_text(
        generate_content_ref_html, encoding="utf-8"
    )
    write_json(
        DOCS_DIR / "generate-content-reference.json",
        parse_generate_content_reference_html(generate_content_ref_html),
    )

    file_search_stores_ref_html = fetch_text(FILE_SEARCH_STORES_REF_URL)
    (DOCS_DIR / "file-search-stores-reference.html").write_text(
        file_search_stores_ref_html, encoding="utf-8"
    )
    write_json(
        DOCS_DIR / "file-search-stores-reference.json",
        parse_file_search_stores_reference_html(file_search_stores_ref_html),
    )

    file_search_documents_ref_html = fetch_text(FILE_SEARCH_DOCUMENTS_REF_URL)
    (DOCS_DIR / "file-search-documents-reference.html").write_text(
        file_search_documents_ref_html, encoding="utf-8"
    )
    write_json(
        DOCS_DIR / "file-search-documents-reference.json",
        parse_file_search_documents_reference_html(file_search_documents_ref_html),
    )

    compat_html = fetch_text(OPENAI_COMPAT_URL)
    (DOCS_DIR / "openai-compat.html").write_text(compat_html, encoding="utf-8")

    openai_yaml = fetch_text(OPENAI_UPSTREAM_SPEC_URL)
    (OPENAI_DIR / "openapi.yaml").write_text(openai_yaml, encoding="utf-8")

    print(f"Saved discovery export to {DISCOVERY_DIR / 'openapi3_0.json'}")
    print(f"Saved docs snapshot to {DOCS_DIR / 'all-methods.html'}")
    print(f"Parsed {len(operations)} documented operations")
    print(f"Saved Files guide snapshot to {DOCS_DIR / 'files-guide.html'}")
    print(f"Saved Batch guide snapshot to {DOCS_DIR / 'batch-guide.html'}")
    print(f"Saved Models reference snapshot to {DOCS_DIR / 'models-reference.html'}")
    print(f"Saved Tokens reference snapshot to {DOCS_DIR / 'tokens-reference.html'}")
    print(
        f"Saved Generate Content reference snapshot to "
        f"{DOCS_DIR / 'generate-content-reference.html'}"
    )
    print(
        f"Saved File Search Stores reference snapshot to "
        f"{DOCS_DIR / 'file-search-stores-reference.html'}"
    )
    print(
        f"Saved File Search Documents reference snapshot to "
        f"{DOCS_DIR / 'file-search-documents-reference.html'}"
    )
    print(f"Saved OpenAI compatibility docs to {DOCS_DIR / 'openai-compat.html'}")
    print(f"Saved OpenAI upstream spec to {OPENAI_DIR / 'openapi.yaml'}")


if __name__ == "__main__":
    main()
