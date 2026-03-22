#!/usr/bin/env python3

from __future__ import annotations

import ast
from collections import defaultdict
from pathlib import Path

from _gemini_common import REPORTS_DIR, ROOT, write_json


def _is_vertexai_test(node: ast.AST) -> bool:
    return (
        isinstance(node, ast.Attribute)
        and node.attr == "vertexai"
        and isinstance(node.value, ast.Attribute)
        and node.value.attr == "_api_client"
        and isinstance(node.value.value, ast.Name)
        and node.value.value.id == "self"
    )


def _branch_modes(test: ast.AST, inherited_mode: str) -> tuple[str, str]:
    if _is_vertexai_test(test):
        return "vertexai", "developer_api"
    if isinstance(test, ast.UnaryOp) and isinstance(test.op, ast.Not) and _is_vertexai_test(test.operand):
        return "developer_api", "vertexai"
    return inherited_mode, inherited_mode


def _expr_to_fragment(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "format_map"
    ):
        return _expr_to_fragment(node.func.value)
    if isinstance(node, ast.JoinedStr):
        parts: list[str] = []
        for value in node.values:
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                parts.append(value.value)
            elif isinstance(value, ast.FormattedValue):
                placeholder = ast.unparse(value.value).strip()
                parts.append("{" + placeholder + "}")
            else:
                return None
        return "".join(parts)
    return None


def _classify_record(branch_mode: str) -> str:
    if branch_mode == "developer_api":
        return "developer_api_only"
    if branch_mode == "vertexai":
        return "vertexai_only"
    return "shared_helper"


def _record_path_assignment(
    statement: ast.stmt,
    function_name: str | None,
    branch_mode: str,
    records: list[dict[str, object]],
) -> None:
    targets: list[ast.expr] = []
    value: ast.AST | None = None

    if isinstance(statement, ast.Assign):
        targets = statement.targets
        value = statement.value
    elif isinstance(statement, ast.AnnAssign):
        targets = [statement.target]
        value = statement.value
    else:
        return

    if value is None:
        return

    if not any(isinstance(target, ast.Name) and target.id == "path" for target in targets):
        return

    fragment = _expr_to_fragment(value)
    if fragment is None:
        return
    if fragment.startswith("{path}?"):
        return

    records.append(
        {
            "branch": branch_mode,
            "classification": _classify_record(branch_mode),
            "function": function_name,
            "line": statement.lineno,
            "path_fragment": fragment,
        }
    )


def _visit_statements(
    statements: list[ast.stmt],
    function_name: str | None,
    branch_mode: str,
    records: list[dict[str, object]],
) -> None:
    for statement in statements:
        if isinstance(statement, ast.ClassDef):
            _visit_statements(statement.body, function_name, branch_mode, records)
            continue

        if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef)):
            _visit_statements(statement.body, statement.name, branch_mode, records)
            continue

        if isinstance(statement, ast.If):
            body_mode, else_mode = _branch_modes(statement.test, branch_mode)
            _visit_statements(statement.body, function_name, body_mode, records)
            _visit_statements(statement.orelse, function_name, else_mode, records)
            continue

        _record_path_assignment(statement, function_name, branch_mode, records)


def main() -> None:
    sdk_root = ROOT / "reference" / "python-genai" / "google" / "genai"
    if not sdk_root.exists():
        raise SystemExit(
            "Missing reference/python-genai submodule. Run `git submodule update --init --recursive` first."
        )

    module_path_fragments: dict[str, list[str]] = {}
    module_path_records: dict[str, list[dict[str, object]]] = {}
    developer_api_only_modules: list[str] = []
    developer_api_modules: list[str] = []
    mixed_surface_modules: list[str] = []
    mixed_with_shared_helper_modules: list[str] = []
    module_classifications: dict[str, str] = {}
    vertexai_only_modules: list[str] = []

    for path in sorted(sdk_root.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        records: list[dict[str, object]] = []
        _visit_statements(tree.body, None, "shared", records)

        if not records:
            continue

        deduped_records = sorted(
            {
                (
                    record["path_fragment"],
                    record["branch"],
                    record["function"],
                    record["line"],
                ): record
                for record in records
            }.values(),
            key=lambda item: (
                str(item["function"] or ""),
                str(item["branch"]),
                str(item["path_fragment"]),
                int(item["line"]),
            ),
        )

        module_path_records[path.name] = deduped_records
        module_path_fragments[path.name] = sorted(
            {str(record["path_fragment"]) for record in deduped_records}
        )

        classifications = {str(record["classification"]) for record in deduped_records}
        if "developer_api_only" in classifications:
            developer_api_modules.append(path.name)
        if classifications == {"developer_api_only"}:
            developer_api_only_modules.append(path.name)
            module_classifications[path.name] = "developer_api_only"
        elif classifications == {"vertexai_only"}:
            vertexai_only_modules.append(path.name)
            module_classifications[path.name] = "vertexai_only"
        elif "shared_helper" in classifications:
            mixed_with_shared_helper_modules.append(path.name)
            module_classifications[path.name] = "mixed_with_shared_helper"
        else:
            mixed_surface_modules.append(path.name)
            module_classifications[path.name] = "mixed_surface"

    write_json(
        REPORTS_DIR / "python-genai-surface.json",
        {
            "developer_api_modules": sorted(set(developer_api_modules)),
            "developer_api_only_modules": sorted(set(developer_api_only_modules)),
            "module_count": len(module_path_records),
            "module_classifications": dict(sorted(module_classifications.items())),
            "module_path_fragments": module_path_fragments,
            "module_path_records": module_path_records,
            "mixed_surface_modules": sorted(set(mixed_surface_modules)),
            "mixed_with_shared_helper_modules": sorted(
                set(mixed_with_shared_helper_modules)
            ),
            "vertexai_only_modules": sorted(set(vertexai_only_modules)),
        },
    )

    print(f"Saved SDK surface report to {REPORTS_DIR / 'python-genai-surface.json'}")


if __name__ == "__main__":
    main()
