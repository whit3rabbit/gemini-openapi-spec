"""Tests for HTML parsing functions in _gemini_common."""

from _gemini_common import (
    DocOperation,
    extract_text_lines,
    parse_all_methods_html,
    parse_files_guide_html,
    parse_batch_guide_html,
    slugify_resource,
    build_operation_id,
    canonical_operation_key,
)


class TestTextExtractor:
    def test_strips_tags(self):
        lines = extract_text_lines("<p>Hello <b>world</b></p>")
        assert "Hello" in lines
        assert "world" in lines

    def test_unescapes_entities(self):
        lines = extract_text_lines("<p>foo &amp; bar</p>")
        assert "foo & bar" in lines

    def test_empty_html(self):
        assert extract_text_lines("") == []

    def test_whitespace_only_skipped(self):
        lines = extract_text_lines("<p>   </p><p>data</p>")
        assert lines == ["data"]


class TestParseAllMethodsHtml:
    """Minimal HTML fixture that mimics the all-methods page structure."""

    FIXTURE = (
        "<p>REST Resource:</p>"
        "<p>v1beta.models</p>"
        "<p>Methods</p>"
        "<p>generateContent</p>"
        "<p>POST /v1beta/{model=models/*}:generateContent</p>"
        "<p>Generates a model response.</p>"
    )

    def test_parses_single_operation(self):
        ops = parse_all_methods_html(self.FIXTURE)
        assert len(ops) == 1
        op = ops[0]
        assert op.resource == "v1beta.models"
        assert op.name == "generateContent"
        assert op.method == "POST"
        assert op.raw_path == "/v1beta/{model=models/*}:generateContent"
        assert op.normalized_path == "/v1beta/models/{model}:generateContent"
        assert op.description == "Generates a model response."

    def test_multiple_operations(self):
        html = (
            "<p>REST Resource:</p>"
            "<p>v1beta.models</p>"
            "<p>Methods</p>"
            "<p>list</p>"
            "<p>GET /v1beta/models</p>"
            "<p>Lists available models.</p>"
            "<p>get</p>"
            "<p>GET /v1beta/{name=models/*}</p>"
            "<p>Gets a model.</p>"
        )
        ops = parse_all_methods_html(html)
        assert len(ops) == 2
        assert ops[0].name == "list"
        assert ops[1].name == "get"

    def test_multiple_resources(self):
        html = (
            "<p>REST Resource:</p>"
            "<p>v1beta.models</p>"
            "<p>Methods</p>"
            "<p>list</p>"
            "<p>GET /v1beta/models</p>"
            "<p>Lists models.</p>"
            "<p>REST Resource:</p>"
            "<p>v1beta.files</p>"
            "<p>Methods</p>"
            "<p>delete</p>"
            "<p>DELETE /v1beta/{name=files/*}</p>"
            "<p>Deletes a file.</p>"
        )
        ops = parse_all_methods_html(html)
        assert len(ops) == 2
        assert ops[0].resource == "v1beta.models"
        assert ops[1].resource == "v1beta.files"


class TestParseFilesGuideHtml:
    def test_detects_upload_alias(self):
        html = '<p>POST /upload/v1beta/files with metadata</p>'
        result = parse_files_guide_html(html)
        assert len(result["documented_aliases"]) == 1
        assert result["documented_aliases"][0]["path"] == "/upload/v1beta/files"

    def test_no_upload_alias(self):
        result = parse_files_guide_html("<p>No upload info here</p>")
        assert result["documented_aliases"] == []

    def test_download_policy(self):
        html = "<p>Note: you can't download the files using the API.</p>"
        result = parse_files_guide_html(html)
        assert result["download_policy"]["download_allowed"] is False


class TestParseBatchGuideHtml:
    def test_detects_download_route(self):
        html = (
            "<p>https://generativelanguage.googleapis.com/download/v1beta/</p>"
            "<p>$responses_file_name</p>"
            "<p>:download?alt</p>"
            "<p>=</p>"
            "<p>media</p>"
        )
        result = parse_batch_guide_html(html)
        assert len(result["documented_operations"]) == 1
        op = result["documented_operations"][0]
        assert op["method"] == "GET"
        assert "download" in op["normalized_path"]

    def test_no_download_route(self):
        result = parse_batch_guide_html("<p>Some batch info</p>")
        assert result["documented_operations"] == []


class TestHelperFunctions:
    def test_slugify_resource(self):
        assert slugify_resource("v1beta.models") == "v1beta_models"

    def test_build_operation_id(self):
        op = DocOperation(
            resource="v1beta.models",
            name="generateContent",
            method="POST",
            raw_path="/v1beta/{model=models/*}:generateContent",
            normalized_path="/v1beta/models/{model}:generateContent",
            description="",
            path_parameters=[],
        )
        assert build_operation_id(op) == "v1beta_models_generateContent"

    def test_canonical_operation_key(self):
        assert canonical_operation_key("post", "/v1beta/files") == "POST /v1beta/files"
