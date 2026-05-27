# Data Quality Contracts Lab

## Problem

Analytics tables should not accept data that breaks basic contracts.

This project validates SaaS billing datasets before they are used by downstream reports.

## Data Flow

CSV datasets -> JSON contracts -> validators -> Markdown report

Failed rows -> quarantine folder

## Design Choices

- Contracts are plain JSON files.
- The validator uses only the Python standard library.
- Checks fail fast enough for CI but still write a report.
- Quarantine output keeps failed rows available for review.

## How To Run

```bash
python -m pip install -e ".[dev]"
python -m pytest
python -m data_quality_contracts_lab.cli --contracts contracts --data data/sample --report reports/validation_report.md --quarantine quarantine
```

The CLI exits with code `1` when any contract fails.

On Windows without installing the package, set `PYTHONPATH=src` before running the CLI.

## Tests

The tests cover contract loading, required fields, duplicate keys, quarantine output, reports, and the CLI path.

## Production Notes

- Contracts should be versioned with the pipeline that consumes the dataset.
- Failed rows should notify the owning team.
- Historical validation results should be stored for trend analysis.
- Freshness and referential checks can be added once source ownership is clear.

## Docs

- [Architecture](docs/architecture.md)

## Portuguese

Este projeto valida datasets de billing SaaS antes do uso em analytics.

Ele usa contratos JSON, gera relatorio Markdown e separa linhas com falha em quarantine.
