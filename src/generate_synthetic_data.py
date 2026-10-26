"""Generate synthetic healthcare equipment operations data for HealthOps Intelligence."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
RNG = np.random.default_rng(42)

SITES = ["Chennai GBS", "Hyderabad Hub", "Pune Depot", "Bengaluru Lab"]
EQUIP_TYPES = ["MRI", "CT", "Ultrasound", "Patient Monitor", "Ventilator", "X-Ray"]
PRIORITIES = ["Critical", "High", "Medium", "Low"]
STATUSES = ["Open", "In Progress", "Resolved", "Closed"]


def _timestamps(n: int, start: str = "2025-01-01", end: str = "2025-09-30") -> pd.Series:
    start_ts = pd.Timestamp(start)
    end_ts = pd.Timestamp(end)
    delta = (end_ts - start_ts).total_seconds()
    offsets = RNG.uniform(0, delta, size=n)
    return pd.Series([start_ts + pd.Timedelta(seconds=float(o)) for o in offsets])


def build_equipment(n: int = 48) -> pd.DataFrame:
    rows = []
    for i in range(1, n + 1):
        rows.append(
            {
                "equipment_id": f"EQ-{i:04d}",
                "equipment_name": f"{RNG.choice(EQUIP_TYPES)}-{i:02d}",
                "equipment_type": RNG.choice(EQUIP_TYPES),
                "site": RNG.choice(SITES),
                "install_date": _timestamps(1, "2020-01-01", "2024-12-01").iloc[0].date(),
                "status": RNG.choice(["Active", "Active", "Active", "Maintenance"]),
            }
        )
    return pd.DataFrame(rows)


def build_service_requests(equipment: pd.DataFrame, n: int = 420) -> pd.DataFrame:
    eq_ids = equipment["equipment_id"].tolist()
    # Inject a few bad refs / quality issues for the SQL checks to catch
    dirty_ids = eq_ids + ["EQ-9999", "EQ-0000", None]
    opened = _timestamps(n)
    resolve_hours = RNG.integers(2, 96, size=n)
    # Force some SLA breaches and missing values
    resolve_hours[::17] = RNG.integers(100, 180, size=len(resolve_hours[::17]))
    closed = opened + pd.to_timedelta(resolve_hours, unit="h")
    closed[::23] = pd.NaT

    df = pd.DataFrame(
        {
            "ticket_id": [f"SR-{i:05d}" for i in range(1, n + 1)],
            "equipment_id": RNG.choice(dirty_ids, size=n),
            "priority": RNG.choice(PRIORITIES, size=n, p=[0.1, 0.25, 0.4, 0.25]),
            "status": RNG.choice(STATUSES, size=n, p=[0.15, 0.2, 0.35, 0.3]),
            "opened_at": opened,
            "resolved_at": closed,
            "sla_hours": RNG.choice([24, 48, 72, 96], size=n, p=[0.25, 0.35, 0.25, 0.15]),
            "issue_category": RNG.choice(
                ["Hardware", "Calibration", "Software", "Consumable", "Network"], size=n
            ),
        }
    )
    # Duplicate a few tickets for quality checks
    dup = df.sample(6, random_state=7).copy()
    df = pd.concat([df, dup], ignore_index=True)
    return df


def build_downtime(equipment: pd.DataFrame, n: int = 260) -> pd.DataFrame:
    eq_ids = equipment["equipment_id"].tolist()
    # Make a few assets repeatedly fail (for anomaly detection)
    hot = eq_ids[:5]
    weighted = hot * 8 + eq_ids
    start = _timestamps(n)
    hours = RNG.uniform(0.5, 18, size=n)
    hours[:20] = RNG.uniform(24, 60, size=20)  # extreme downtime outliers
    end = start + pd.to_timedelta(hours, unit="h")
    # Invalid: end before start on some rows
    end.iloc[11] = start.iloc[11] - pd.Timedelta(hours=3)
    end.iloc[29] = pd.NaT

    return pd.DataFrame(
        {
            "downtime_id": [f"DT-{i:05d}" for i in range(1, n + 1)],
            "equipment_id": RNG.choice(weighted, size=n),
            "started_at": start,
            "ended_at": end,
            "reason": RNG.choice(
                ["Unplanned failure", "Preventive maintenance", "Parts wait", "Power issue"],
                size=n,
            ),
        }
    )


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    equipment = build_equipment()
    tickets = build_service_requests(equipment)
    downtime = build_downtime(equipment)

    equipment.to_csv(RAW / "equipment.csv", index=False)
    tickets.to_csv(RAW / "service_requests.csv", index=False)
    downtime.to_csv(RAW / "downtime_events.csv", index=False)
    print(f"Wrote synthetic raw tables to {RAW}")
    print(f"  equipment: {len(equipment)} rows")
    print(f"  service_requests: {len(tickets)} rows")
    print(f"  downtime_events: {len(downtime)} rows")


if __name__ == "__main__":
    main()
