"""Flag unusual downtime patterns and recurring equipment failures."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"


def detect() -> pd.DataFrame:
    dt = pd.read_csv(PROCESSED / "downtime_events.csv", parse_dates=["started_at", "ended_at"])
    dt = dt.dropna(subset=["downtime_hours"])

    # Per-equipment failure counts and downtime totals
    summary = (
        dt.groupby("equipment_id", as_index=False)
        .agg(
            event_count=("downtime_id", "count"),
            total_downtime_hours=("downtime_hours", "sum"),
            avg_downtime_hours=("downtime_hours", "mean"),
            max_downtime_hours=("downtime_hours", "max"),
        )
    )

    # Robust thresholds
    count_cut = summary["event_count"].quantile(0.85)
    hour_cut = summary["avg_downtime_hours"].median() + 1.5 * summary["avg_downtime_hours"].std(ddof=0)

    summary["recurring_failure_flag"] = summary["event_count"] >= max(count_cut, 3)
    summary["unusual_downtime_flag"] = summary["avg_downtime_hours"] >= hour_cut
    summary["anomaly_flag"] = summary["recurring_failure_flag"] | summary["unusual_downtime_flag"]
    summary["anomaly_reason"] = np.where(
        summary["recurring_failure_flag"] & summary["unusual_downtime_flag"],
        "Recurring failures + elevated average downtime",
        np.where(
            summary["recurring_failure_flag"],
            "Recurring equipment failures",
            np.where(summary["unusual_downtime_flag"], "Unusual downtime pattern", ""),
        ),
    )
    return summary.sort_values(["anomaly_flag", "event_count"], ascending=[False, False])


def main() -> None:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    anomalies = detect()
    anomalies.to_csv(PROCESSED / "equipment_anomaly_flags.csv", index=False)
    flagged = anomalies[anomalies["anomaly_flag"]]
    print(f"Flagged {len(flagged)} / {len(anomalies)} equipment assets")
    if not flagged.empty:
        print(flagged[["equipment_id", "event_count", "avg_downtime_hours", "anomaly_reason"]].head(10).to_string(index=False))
    print(f"Wrote {PROCESSED / 'equipment_anomaly_flags.csv'}")


if __name__ == "__main__":
    main()
