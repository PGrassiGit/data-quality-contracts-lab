from pathlib import Path

from data_quality_contracts_lab.cli import run


def test_cli_run_writes_report(tmp_path: Path) -> None:
    report_path = tmp_path / "report.md"
    quarantine_dir = tmp_path / "quarantine"

    exit_code = run(
        contracts_dir=Path("contracts"),
        data_dir=Path("data/sample"),
        report_path=report_path,
        quarantine_dir=quarantine_dir,
    )

    assert exit_code == 0
    assert "Validation Report" in report_path.read_text(encoding="utf-8")


def test_cli_run_fails_bad_dataset_and_writes_quarantine(tmp_path: Path) -> None:
    report_path = tmp_path / "report.md"
    quarantine_dir = tmp_path / "quarantine"

    exit_code = run(
        contracts_dir=Path("contracts"),
        data_dir=Path("data/bad"),
        report_path=report_path,
        quarantine_dir=quarantine_dir,
    )

    assert exit_code == 1
    assert "missing reference" in report_path.read_text(encoding="utf-8")
    assert (quarantine_dir / "invoices_failed.csv").exists()
