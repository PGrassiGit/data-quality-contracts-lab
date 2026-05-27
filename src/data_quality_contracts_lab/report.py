from __future__ import annotations

from pathlib import Path

from data_quality_contracts_lab.validator import ValidationResult


def render_report(results: list[ValidationResult]) -> str:
    lines = ["# Validation Report", ""]
    for result in results:
        status = "pass" if result.passed else "fail"
        lines.extend(
            [
                f"## {result.dataset}",
                "",
                f"- status: {status}",
                f"- rows read: {result.rows_read}",
                f"- issue count: {len(result.issues)}",
                "",
            ]
        )
        for issue in result.issues:
            lines.append(f"- row {issue.row_number}, {issue.field}: {issue.message}")
        if result.issues:
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_report(results: list[ValidationResult], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_report(results), encoding="utf-8")
    return path
