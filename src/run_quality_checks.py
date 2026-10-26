"""SQL-equivalent data-quality checks implemented in pandas for portability.

Mirrors the rules in sql/02_quality_checks.sql so the pipeline runs without a DB.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"


def load_raw() -> dict[str, pd.DataFrame]:
    return {
        "equipment": pd.read_csv(RAW / "equipment.csv"),
        "service_requests": pd.read_csv(RAW / "service_requests.csv", parse_dates=["opened_at", "resolved_at"]),
        "downtime_events": pd.read_csv(RAW / "downtime_events.csv", parse_dates=["started_at", "ended_at"]),
    }


def quality_report(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    eq = tables["equipment"]
    sr = tables["service_requests"]
    dt = tables["downtime_events"]
    valid_eq = set(eq["equipment_id"])

    checks = []

    dup_tickets = int(sr["ticket_id"].duplicated().sum())
    checks.append(("duplicate_service_tickets", dup_tickets, "service_requests.ticket_id"))

    missing_eq = int(sr["equipment_id"].isna().sum())
    checks.append(("missing_equipment_on_ticket", missing_eq, "service_requests.equipment_id"))

    bad_ref = int((~sr["equipment_id"].isna() & ~sr["equipment_id"].isin(valid_eq)).sum())
    checks.append(("invalid_equipment_reference", bad_ref, "service_requests.equipment_id"))

    missing_resolved = int(sr["resolved_at"].isna().sum())
    checks.append(("missing_resolved_timestamp", missing_resolved, "service_requests.resolved_at"))

    invalid_order = int((sr["resolved_at"].notna() & (sr["resolved_at"] < sr["opened_at"])).sum())
    checks.append(("resolved_before_opened", invalid_order, "service_requests timestamps"))

    missing_dt_end = int(dt["ended_at"].isna().sum())
    checks.append(("missing_downtime_end", missing_dt_end, "downtime_events.ended_at"))

    bad_dt_order = int((dt["ended_at"].notna() & (dt["ended_at"] < dt["started_at"])).sum())
    checks.append(("downtime_end_before_start", bad_dt_order, "downtime_events timestamps"))

    bad_dt_ref = int((~dt["equipment_id"].isin(valid_eq)).sum())
    checks.append(("invalid_downtime_equipment_ref", bad_dt_ref, "downtime_events.equipment_id"))

    return pd.DataFrame(checks, columns=["check_name", "issue_count", "field_scope"])


def clean_tables(tables: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    eq = tables["equipment"].copy()
    sr = tables["service_requests"].drop_duplicates(subset=["ticket_id"]).copy()
    dt = tables["downtime_events"].copy()
    valid_eq = set(eq["equipment_id"])

    sr = sr[sr["equipment_id"].isin(valid_eq)]
    sr = sr[sr["resolved_at"].isna() | (sr["resolved_at"] >= sr["opened_at"])]

    dt = dt[dt["equipment_id"].isin(valid_eq)]
    dt = dt[dt["ended_at"].isna() | (dt["ended_at"] >= dt["started_at"])]

    # Resolution hours for KPI marts
    sr["resolution_hours"] = (sr["resolved_at"] - sr["opened_at"]).dt.total_seconds() / 3600.0
    sr["sla_met"] = sr["resolution_hours"] <= sr["sla_hours"]

    dt["downtime_hours"] = (dt["ended_at"] - dt["started_at"]).dt.total_seconds() / 3600.0

    return {"equipment": eq, "service_requests": sr, "downtime_events": dt}


def main() -> None:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    tables = load_raw()
    report = quality_report(tables)
    cleaned = clean_tables(tables)

    report.to_csv(PROCESSED / "data_quality_report.csv", index=False)
    for name, df in cleaned.items():
        df.to_csv(PROCESSED / f"{name}.csv", index=False)

    print("Data quality report:")
    print(report.to_string(index=False))
    print(f"\nWrote cleaned tables + quality report to {PROCESSED}")


if __name__ == "__main__":
    main()
