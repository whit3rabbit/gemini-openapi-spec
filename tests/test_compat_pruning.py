"""Tests for OpenAI compat schema pruning logic."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from build_openai_compat import _collect_refs, _prune_unreachable_schemas


class TestCollectRefs:
    def test_finds_schema_refs(self):
        obj = {"$ref": "#/components/schemas/Foo"}
        assert _collect_refs(obj) == {"Foo"}

    def test_finds_nested_refs(self):
        obj = {
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/Bar"}
                }
            }
        }
        assert "Bar" in _collect_refs(obj)

    def test_ignores_non_schema_refs(self):
        obj = {"$ref": "#/components/securitySchemes/BearerAuth"}
        assert _collect_refs(obj) == set()

    def test_handles_arrays(self):
        obj = [{"$ref": "#/components/schemas/A"}, {"$ref": "#/components/schemas/B"}]
        assert _collect_refs(obj) == {"A", "B"}


class TestPruneUnreachableSchemas:
    def test_removes_unreachable_schemas(self):
        spec = {
            "paths": {
                "/foo": {
                    "get": {
                        "responses": {
                            "200": {
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": "#/components/schemas/Used"}
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "components": {
                "schemas": {
                    "Used": {"type": "object"},
                    "Orphan": {"type": "object"},
                }
            },
        }
        removed = _prune_unreachable_schemas(spec)
        assert removed == 1
        assert "Used" in spec["components"]["schemas"]
        assert "Orphan" not in spec["components"]["schemas"]

    def test_follows_transitive_refs(self):
        spec = {
            "paths": {
                "/bar": {
                    "post": {
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Root"}
                                }
                            }
                        },
                        "responses": {},
                    }
                }
            },
            "components": {
                "schemas": {
                    "Root": {
                        "type": "object",
                        "properties": {
                            "child": {"$ref": "#/components/schemas/Child"},
                        },
                    },
                    "Child": {"type": "object"},
                    "Unreachable": {"type": "string"},
                }
            },
        }
        removed = _prune_unreachable_schemas(spec)
        assert removed == 1
        assert "Root" in spec["components"]["schemas"]
        assert "Child" in spec["components"]["schemas"]
        assert "Unreachable" not in spec["components"]["schemas"]

    def test_keeps_gemini_prefixed_schemas(self):
        spec = {
            "paths": {},
            "components": {
                "schemas": {
                    "GeminiCustom": {"type": "object"},
                    "Orphan": {"type": "string"},
                }
            },
        }
        removed = _prune_unreachable_schemas(spec)
        assert removed == 1
        assert "GeminiCustom" in spec["components"]["schemas"]
        assert "Orphan" not in spec["components"]["schemas"]

    def test_no_schemas_is_noop(self):
        spec = {"paths": {}, "components": {}}
        assert _prune_unreachable_schemas(spec) == 0
