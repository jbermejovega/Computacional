from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

MARKER = "FISICA_COMPUTACIONAL_DEEP_NOTEBOOK_REVIEW_V1"
RESOURCE_ID = "MCP_SCIKI_N8N_FISICA_COMPUTACIONAL_REVIEW_RESOURCE_V1"
ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "build" / "revision_fisica_computacional"

NOTEBOOK_PATHS = [
    "Obligatorio4.ipynb",
    "Voluntarios/Voluntario1/notebook.ipynb",
    "obligatorios/obligatorio1/sistemas_solar_notebook.ipynb",
    "obligatorios/obligatorio2/Informe _ising.ipynb",
    "obligatorios/obligatorio2/Obligatorio2_informe.ipynb",
    "obligatorios/obligatorio4/Obligatorio4.ipynb",
]

IMPORT_RE = re.compile(r"^\s*(import\s+\S+|from\s+\S+\s+import\s+)")
SHELL_RE = re.compile(r"^\s*!|subprocess|os\.system")
FILE_IO_RE = re.compile(
    r"\.(dat|txt|csv|png|gif|mp4|cpp)|open\(|loadtxt|read_csv|savetxt|savefig"
)
EXTERNAL_DEP_RE = re.compile(r"pip install|apt-get|conda install|wget|curl")
HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+")


def cell_source(cell: dict[str, Any]) -> str:
    source = cell.get("source", "")
    if isinstance(source, list):
        return "".join(str(part) for part in source)
    return str(source)


def unique_first(values: list[str], limit: int) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
        if len(result) >= limit:
            break
    return result


def summarize_notebook(path_text: str) -> dict[str, Any]:
    path = ROOT / path_text
    if not path.exists():
        return {
            "path": path_text,
            "status": "missing_file",
            "review_state": "BLOCKED",
            "risks": ["missing notebook file"],
        }

    raw = path.read_bytes()
    if not raw.strip():
        return {
            "path": path_text,
            "status": "empty_file",
            "review_state": "BLOCKED",
            "bytes": 0,
            "cells": 0,
            "markdown_cells": 0,
            "code_cells": 0,
            "headings": [],
            "imports": [],
            "error_outputs": 0,
            "executed_code_cells": 0,
            "empty_code_cells": 0,
            "long_code_cells": [],
            "shell_commands": [],
            "file_io_mentions": [],
            "external_deps": [],
            "source_hash": None,
            "risks": ["empty notebook file"],
        }

    try:
        notebook = json.loads(raw.decode("utf-8"))
    except Exception as exc:  # pragma: no cover - diagnostic path for CI witness only.
        return {
            "path": path_text,
            "status": "parse_error",
            "review_state": "BLOCKED",
            "bytes": len(raw),
            "error": str(exc),
            "risks": ["notebook json parse error"],
        }

    cells = list(notebook.get("cells", []))
    markdown_cells = [cell for cell in cells if cell.get("cell_type") == "markdown"]
    code_cells = [cell for cell in cells if cell.get("cell_type") == "code"]

    headings: list[str] = []
    imports: list[str] = []
    shell_commands: list[str] = []
    file_io_mentions: list[str] = []
    external_deps: list[str] = []
    error_outputs = 0
    executed_code_cells = 0
    empty_code_cells = 0
    long_code_cells: list[int] = []
    source_digest_parts: list[str] = []

    for cell_index, cell in enumerate(cells, start=1):
        source = cell_source(cell)
        source_digest_parts.append(f"{cell.get('cell_type')}\0{source}")

        if cell.get("cell_type") == "markdown":
            for line in source.splitlines():
                if HEADING_RE.match(line):
                    headings.append(line.strip())
            continue

        if cell.get("cell_type") != "code":
            continue

        lines = source.splitlines()
        if not source.strip():
            empty_code_cells += 1
        if len(lines) > 80:
            long_code_cells.append(cell_index)
        if cell.get("execution_count") is not None:
            executed_code_cells += 1

        for line in lines:
            text = line.strip()
            if IMPORT_RE.match(text):
                imports.append(text)
            if SHELL_RE.search(text):
                shell_commands.append(text)
            if FILE_IO_RE.search(text):
                file_io_mentions.append(text)
            if EXTERNAL_DEP_RE.search(text):
                external_deps.append(text)

        for output in cell.get("outputs", []):
            if output.get("output_type") == "error":
                error_outputs += 1

    risks: list[str] = []
    if error_outputs:
        risks.append("saved error outputs present")
    if not headings and markdown_cells:
        risks.append("markdown lacks explicit section headings")
    if empty_code_cells:
        risks.append("empty code cells present")
    if long_code_cells:
        risks.append("long code cells should be split or moved to scripts")
    if executed_code_cells != len(code_cells):
        risks.append("not all code cells have execution_count")
    if shell_commands:
        risks.append("requires local shell/C++ execution")
    if file_io_mentions:
        risks.append("depends on generated files or media artifacts")
    if external_deps:
        risks.append("runtime dependency installation commands present")

    review_state = "READY_FOR_CONTENT_REVIEW"
    if risks:
        review_state = "NEEDS_REVISION"

    return {
        "path": path_text,
        "status": "parsed",
        "review_state": review_state,
        "bytes": len(raw),
        "cells": len(cells),
        "markdown_cells": len(markdown_cells),
        "code_cells": len(code_cells),
        "headings": unique_first(headings, 20),
        "imports": unique_first(imports, 25),
        "error_outputs": error_outputs,
        "executed_code_cells": executed_code_cells,
        "empty_code_cells": empty_code_cells,
        "long_code_cells": long_code_cells,
        "shell_commands": unique_first(shell_commands, 20),
        "file_io_mentions": unique_first(file_io_mentions, 30),
        "external_deps": unique_first(external_deps, 20),
        "source_hash": hashlib.sha256("".join(source_digest_parts).encode("utf-8")).hexdigest(),
        "risks": risks,
    }


def attach_duplicate_groups(summaries: list[dict[str, Any]]) -> None:
    groups: dict[str, list[str]] = {}
    for summary in summaries:
        digest = summary.get("source_hash")
        if not digest:
            continue
        groups.setdefault(str(digest), []).append(str(summary["path"]))

    duplicate_groups = [paths for paths in groups.values() if len(paths) > 1]
    for summary in summaries:
        for paths in duplicate_groups:
            if summary["path"] in paths:
                summary.setdefault("risks", []).append(
                    "duplicate notebook source group: " + ", ".join(paths)
                )
                if summary.get("review_state") == "READY_FOR_CONTENT_REVIEW":
                    summary["review_state"] = "NEEDS_REVISION"


def build_witness(summaries: list[dict[str, Any]]) -> dict[str, Any]:
    blocked = [item for item in summaries if item.get("review_state") == "BLOCKED"]
    needs_revision = [item for item in summaries if item.get("review_state") == "NEEDS_REVISION"]
    ready = [item for item in summaries if item.get("review_state") == "READY_FOR_CONTENT_REVIEW"]
    return {
        "marker": MARKER,
        "resource_id": RESOURCE_ID,
        "resource_active": True,
        "repo": "jbermejovega/Computacional",
        "scope": "fisica_computacional_exams_notebook_by_notebook",
        "workflow": ".github/workflows/fisica-computacional-notebook-review.yml",
        "review_mode": "read_only_static_notebook_json_review",
        "code_execution_allowed": False,
        "notebook_count": len(summaries),
        "blocked_count": len(blocked),
        "needs_revision_count": len(needs_revision),
        "ready_count": len(ready),
        "invariants": {
            "mcp_resource_active": True,
            "sciki_map_active": True,
            "n8n_workflow_exported": True,
            "notebook_by_notebook": True,
            "no_notebook_code_execution": True,
            "replay_safe": True,
            "contents_read_only": True,
        },
        "notebooks": summaries,
    }


def write_markdown(witness: dict[str, Any]) -> None:
    lines = [
        f"# {MARKER}",
        "",
        "Generated witness for the MCP/SCIKI/N8N invariant review workflow.",
        "Notebook code is not executed by this script.",
        "",
        "| Notebook | State | Cells | Markdown | Code | Risks |",
        "| --- | --- | ---: | ---: | ---: | --- |",
    ]
    for item in witness["notebooks"]:
        risks = "; ".join(item.get("risks", [])) or "none"
        risks = risks.replace("|", "/")
        lines.append(
            "| `{path}` | {state} | {cells} | {md} | {code} | {risks} |".format(
                path=item["path"],
                state=item.get("review_state", item.get("status")),
                cells=item.get("cells", 0),
                md=item.get("markdown_cells", 0),
                code=item.get("code_cells", 0),
                risks=risks,
            )
        )
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- blocked_count: {witness['blocked_count']}")
    lines.append(f"- needs_revision_count: {witness['needs_revision_count']}")
    lines.append(f"- ready_count: {witness['ready_count']}")
    lines.append("- resource_active: true")
    lines.append("- replay_safe: true")
    (OUTPUT_DIR / "notebook-review-witness.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    summaries = [summarize_notebook(path) for path in NOTEBOOK_PATHS]
    attach_duplicate_groups(summaries)
    witness = build_witness(summaries)

    (OUTPUT_DIR / "notebook-review-witness.json").write_text(
        json.dumps(witness, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_markdown(witness)
    print(json.dumps(witness, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
