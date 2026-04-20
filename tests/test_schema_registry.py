"""Tests for native_schema_registry.py."""

from native_schema_registry import build_native_components, selected_native_operation_keys


class TestBuildNativeComponents:
    def test_returns_dict(self):
        components = build_native_components()
        assert isinstance(components, dict)

    def test_has_core_schemas(self):
        components = build_native_components()
        expected = [
            "Content",
            "Part",
            "GenerateContentRequest",
            "GenerateContentResponse",
            "GenerateContentCandidate",
            "CachedContent",
            "File",
            "EmbedContentRequest",
            "EmbedContentResponse",
        ]
        for name in expected:
            assert name in components, f"Missing schema: {name}"

    def test_generation_config_response_schema_refs_api_schema(self):
        components = build_native_components()
        gen_config = components["GenerationConfig"]
        assert gen_config["properties"]["responseSchema"] == {
            "$ref": "#/components/schemas/ApiSchema"
        }

    def test_no_empty_schemas(self):
        """Every schema should have at least a type or $ref or oneOf."""
        components = build_native_components()
        for name, schema in components.items():
            has_structure = any(
                key in schema
                for key in ("type", "$ref", "oneOf", "anyOf", "allOf", "enum")
            )
            assert has_structure, f"Schema {name} has no structural definition"

    def test_ref_targets_exist(self):
        """All $ref targets within schemas should reference existing components."""
        components = build_native_components()
        prefix = "#/components/schemas/"

        def collect_refs(obj):
            refs = []
            if isinstance(obj, dict):
                if "$ref" in obj:
                    refs.append(obj["$ref"])
                for v in obj.values():
                    refs.extend(collect_refs(v))
            elif isinstance(obj, list):
                for item in obj:
                    refs.extend(collect_refs(item))
            return refs

        all_refs = collect_refs(components)
        for ref in all_refs:
            assert ref.startswith(prefix), f"Unexpected $ref format: {ref}"
            target = ref[len(prefix):]
            assert target in components, f"Dangling $ref: {ref}"


class TestSelectedNativeOperationKeys:
    def test_is_nonempty_set(self):
        keys = selected_native_operation_keys()
        assert isinstance(keys, set)
        assert len(keys) > 0

    def test_keys_are_2_tuples(self):
        """Each key is (method, normalized_path)."""
        for key in selected_native_operation_keys():
            assert isinstance(key, tuple), f"Expected tuple, got {type(key)}"
            assert len(key) == 2, f"Expected 2-tuple, got {len(key)}-tuple: {key}"

    def test_keys_have_valid_methods(self):
        valid_methods = {"GET", "POST", "PATCH", "DELETE", "PUT"}
        for method, path in selected_native_operation_keys():
            assert method in valid_methods, f"Invalid method {method} in key"
