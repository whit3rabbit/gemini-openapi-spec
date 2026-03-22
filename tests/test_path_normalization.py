"""Tests for Google path normalization in _gemini_common.normalize_google_path."""

from _gemini_common import normalize_google_path


class TestNormalizeGooglePath:
    """Known input/output pairs for path expansion."""

    def test_simple_wildcard(self):
        path, params = normalize_google_path("/v1beta/{name=cachedContents/*}")
        assert path == "/v1beta/cachedContents/{cachedContent}"
        assert len(params) == 1
        assert params[0]["openapi_name"] == "cachedContent"

    def test_nested_wildcards(self):
        path, params = normalize_google_path(
            "/v1beta/{name=fileSearchStores/*/documents/*}"
        )
        assert path == "/v1beta/fileSearchStores/{fileSearchStore}/documents/{document}"
        assert len(params) == 2
        assert params[0]["openapi_name"] == "fileSearchStore"
        assert params[1]["openapi_name"] == "document"

    def test_no_binding_pattern(self):
        """Simple {param} without = should stay as-is."""
        path, params = normalize_google_path("/v1beta/models/{model}")
        assert path == "/v1beta/models/{model}"
        assert len(params) == 1
        assert params[0]["openapi_name"] == "model"

    def test_model_wildcard(self):
        path, params = normalize_google_path("/v1beta/{model=models/*}:generateContent")
        assert path == "/v1beta/models/{model}:generateContent"
        assert len(params) == 1
        assert params[0]["openapi_name"] == "model"

    def test_parent_binding(self):
        path, params = normalize_google_path(
            "/v1beta/{parent=fileSearchStores/*}/documents"
        )
        assert path == "/v1beta/fileSearchStores/{fileSearchStore}/documents"
        assert len(params) == 1

    def test_no_parameters(self):
        path, params = normalize_google_path("/v1beta/files")
        assert path == "/v1beta/files"
        assert params == []

    def test_singularize_ies(self):
        """'ies' suffix becomes 'y'."""
        path, params = normalize_google_path("/v1beta/{name=entries/*}")
        assert path == "/v1beta/entries/{entry}"

    def test_singularize_ches(self):
        """'ches' suffix drops 'es'."""
        path, params = normalize_google_path("/v1beta/{name=batches/*}")
        assert path == "/v1beta/batches/{batch}"

    def test_preserves_binding_token(self):
        """Parameters record the original binding token for documentation."""
        _, params = normalize_google_path("/v1beta/{name=files/*}")
        assert params[0]["binding_token"] == "name=files/*"

    def test_upload_path(self):
        path, _ = normalize_google_path(
            "/upload/v1beta/{fileSearchStoreName=fileSearchStores/*}:uploadToFileSearchStore"
        )
        assert path == "/upload/v1beta/fileSearchStores/{fileSearchStore}:uploadToFileSearchStore"

    def test_cached_content_patch_path(self):
        """Dotted parameter name like cachedContent.name."""
        path, params = normalize_google_path(
            "/v1beta/{cachedContent.name=cachedContents/*}"
        )
        assert path == "/v1beta/cachedContents/{cachedContent}"
        assert params[0]["name"] == "cachedContent.name"
