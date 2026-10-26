"""Build a static HTML KPI dashboard + screenshot from processed HealthOps data."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
DEMO = ROOT / "docs" / "demo"
DOCS = ROOT / "docs"


def load() -> dict[str, pd.DataFrame]:
    return {
        "equipment": pd.read_csv(PROCESSED / "equipment.csv"),
        "service_requests": pd.read_csv(
            PROCESSED / "service_requests.csv", parse_dates=["opened_at", "resolved_at"]
        ),
        "downtime_events": pd.read_csv(PROCESSED / "downtime_events.csv"),
        "anomalies": pd.read_csv(PROCESSED / "equipment_anomaly_flags.csv"),
        "quality": pd.read_csv(PROCESSED / "data_quality_report.csv"),
    }


def compute_kpis(tables: dict[str, pd.DataFrame]) -> dict:
    sr = tables["service_requests"]
    dt = tables["downtime_events"]
    eq = tables["equipment"]
    an = tables["anomalies"]
    q = tables["quality"]
    resolved = sr["resolved_at"].notna()
    # SLA % = share of *resolved* tickets where resolution_hours <= ticket sla_hours (24/48/72/96).
    return {
        "equipment_count": int(len(eq)),
        "ticket_count": int(len(sr)),
        "resolved_tickets": int(resolved.sum()),
        "avg_resolution_hours": round(float(sr.loc[resolved, "resolution_hours"].mean()), 2),
        "sla_compliance_pct": round(float(sr.loc[resolved, "sla_met"].mean() * 100), 1),
        "total_downtime_hours": round(float(dt["downtime_hours"].sum()), 1),
        "anomalous_assets": int(an["anomaly_flag"].sum()),
        "quality_issues_caught": int(q["issue_count"].sum()),
        "sla_definition": (
            "Resolved tickets only; sla_met when resolution_hours <= ticket sla_hours "
            "(targets are 24, 48, 72, or 96 hours)."
        ),
    }


def write_verification(kpis: dict, tables: dict[str, pd.DataFrame]) -> None:
    q = tables["quality"]
    lines = [
        "# SQL → analytics KPI verification",
        "",
        "These KPIs are computed from the cleaned tables in `data/processed/` "
        "(same grain Power BI should use after SQL/pandas transforms).",
        "",
        "## Verified KPI values",
        "",
        f"| KPI | Value | Source logic |",
        f"|-----|------:|--------------|",
        f"| Equipment assets | {kpis['equipment_count']} | `COUNT(*)` on equipment |",
        f"| Service tickets (clean) | {kpis['ticket_count']} | de-duplicated + valid equipment refs |",
        f"| Resolved tickets | {kpis['resolved_tickets']} | `resolved_at IS NOT NULL` |",
        f"| Avg resolution hours | {kpis['avg_resolution_hours']} | `AVG(resolution_hours)` on resolved tickets |",
        f"| SLA compliance % | {kpis['sla_compliance_pct']}% | resolved tickets with `resolution_hours <= sla_hours` |",
        f"| Total downtime hours | {kpis['total_downtime_hours']} | `SUM(downtime_hours)` |",
        f"| Anomalous assets | {kpis['anomalous_assets']} | Python anomaly flags |",
        f"| Raw quality issues caught | {kpis['quality_issues_caught']} | sum of quality check counts |",
        "",
        "## SLA definition (interview-ready)",
        "",
        "- **Eligible population:** resolved tickets only (`resolved_at` is present).",
        "- **SLA threshold:** each ticket has its own target in `sla_hours` — one of **24, 48, 72, or 96** hours.",
        "- **Calculation:** `sla_met = resolution_hours <= sla_hours`; compliance % = mean of `sla_met` over resolved tickets.",
        "- **Avg resolution hours:** mean `resolution_hours` over the same resolved population (can exceed the modal SLA target when many tickets breach).",
        "",
        "## Raw data-quality checks (before cleaning)",
        "",
        "| Check | Issues |",
        "|-------|-------:|",
    ]
    for _, row in q.iterrows():
        lines.append(f"| {row['check_name']} | {int(row['issue_count'])} |")
    lines += [
        "",
        "## Power BI alignment",
        "",
        "Implement the DAX measures in `powerbi/dax_measures.md` against these processed tables. "
        "Card values for SLA %, average resolution hours, total downtime, and anomalous assets "
        "should match this verification file after refresh.",
        "",
    ]
    (DOCS / "kpi_verification.md").write_text("\n".join(lines), encoding="utf-8")


def write_screenshot(tables: dict[str, pd.DataFrame], kpis: dict) -> None:
    eq = tables["equipment"]
    dt = tables["downtime_events"].merge(eq[["equipment_id", "site", "equipment_type"]], on="equipment_id", how="left")
    by_site = dt.groupby("site", as_index=False)["downtime_hours"].sum().sort_values("downtime_hours", ascending=False)
    an = tables["anomalies"]
    top = an.sort_values("event_count", ascending=False).head(8)

    fig, axes = plt.subplots(2, 2, figsize=(12, 7), constrained_layout=True)
    fig.suptitle("HealthOps Intelligence — Operations & Quality Dashboard", fontsize=14, fontweight="bold")

    # KPI text panel
    ax = axes[0, 0]
    ax.axis("off")
    kpi_text = (
        f"SLA Compliance: {kpis['sla_compliance_pct']}%\n"
        f"Avg Resolution: {kpis['avg_resolution_hours']} h\n"
        f"Total Downtime: {kpis['total_downtime_hours']} h\n"
        f"Anomalous Assets: {kpis['anomalous_assets']}\n"
        f"Tickets (clean): {kpis['ticket_count']}\n"
        f"Quality Issues Caught: {kpis['quality_issues_caught']}"
    )
    ax.text(0.02, 0.95, "KPI Summary", fontsize=12, fontweight="bold", va="top")
    ax.text(0.02, 0.78, kpi_text, fontsize=11, va="top", family="monospace")

    ax = axes[0, 1]
    ax.barh(by_site["site"], by_site["downtime_hours"], color="#003366")
    ax.set_title("Downtime Hours by Site")
    ax.set_xlabel("Hours")

    ax = axes[1, 0]
    ax.bar(top["equipment_id"], top["event_count"], color="#8B1E3F")
    ax.set_title("Top Equipment by Downtime Events")
    ax.tick_params(axis="x", rotation=45)
    ax.set_ylabel("Events")

    ax = axes[1, 1]
    q = tables["quality"].sort_values("issue_count", ascending=True)
    ax.barh(q["check_name"], q["issue_count"], color="#4A5568")
    ax.set_title("Raw Data-Quality Issues Caught")
    ax.set_xlabel("Issue count")

    DEMO.mkdir(parents=True, exist_ok=True)
    out = DEMO / "dashboard.png"
    fig.savefig(out, dpi=160)
    plt.close(fig)
    print(f"Wrote {out}")


def write_html(kpis: dict) -> None:
    DEMO.mkdir(parents=True, exist_ok=True)
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>HealthOps Intelligence Dashboard</title>
  <style>
    :root {{ --navy:#003366; --bg:#f4f6f8; --card:#fff; --text:#1a1a1a; }}
    body {{ margin:0; font-family: Georgia, 'Times New Roman', serif; background:var(--bg); color:var(--text); }}
    header {{ background:var(--navy); color:#fff; padding:1.25rem 1.5rem; }}
    header h1 {{ margin:0; font-size:1.4rem; letter-spacing:.02em; }}
    header p {{ margin:.35rem 0 0; opacity:.9; font-size:.95rem; }}
    main {{ max-width:1100px; margin:0 auto; padding:1.25rem; }}
    .kpis {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(160px,1fr)); gap:.75rem; }}
    .card {{ background:var(--card); border:1px solid #d8dee6; border-radius:6px; padding:.9rem 1rem; }}
    .card .label {{ font-size:.75rem; text-transform:uppercase; letter-spacing:.04em; color:#555; }}
    .card .value {{ font-size:1.55rem; font-weight:700; color:var(--navy); margin-top:.25rem; }}
    img {{ width:100%; border:1px solid #d8dee6; border-radius:6px; background:#fff; margin-top:1rem; }}
    footer {{ max-width:1100px; margin:0 auto 2rem; padding:0 1.25rem; font-size:.85rem; color:#555; }}
    a {{ color:var(--navy); }}
  </style>
</head>
<body>
  <header>
    <h1>HealthOps Intelligence</h1>
    <p>Healthcare operations &amp; quality analytics — equipment performance, downtime, SLA compliance</p>
  </header>
  <main>
    <div class="kpis">
      <div class="card"><div class="label">SLA Compliance</div><div class="value">{kpis['sla_compliance_pct']}%</div></div>
      <div class="card"><div class="label">Avg Resolution</div><div class="value">{kpis['avg_resolution_hours']} h</div></div>
      <div class="card"><div class="label">Total Downtime</div><div class="value">{kpis['total_downtime_hours']} h</div></div>
      <div class="card"><div class="label">Anomalous Assets</div><div class="value">{kpis['anomalous_assets']}</div></div>
      <div class="card"><div class="label">Clean Tickets</div><div class="value">{kpis['ticket_count']}</div></div>
      <div class="card"><div class="label">Quality Issues Caught</div><div class="value">{kpis['quality_issues_caught']}</div></div>
    </div>
    <img src="dashboard.png" alt="HealthOps Intelligence dashboard screenshot" />
  </main>
  <footer>
    Synthetic healthcare operations dataset.
    Source: <a href="https://github.com/veera-1175/HealthOps-Intelligence">GitHub</a> ·
    KPI checks: <a href="../kpi_verification.md">kpi_verification.md</a> ·
    DAX: <a href="../../powerbi/dax_measures.md">dax_measures.md</a>
  </footer>
  <script type="application/json" id="kpis">{json.dumps(kpis)}</script>
</body>
</html>
"""
    (DEMO / "index.html").write_text(html, encoding="utf-8")
    print(f"Wrote {DEMO / 'index.html'}")


def main() -> None:
    tables = load()
    kpis = compute_kpis(tables)
    write_verification(kpis, tables)
    write_screenshot(tables, kpis)
    write_html(kpis)
    print(json.dumps(kpis, indent=2))


if __name__ == "__main__":
    main()
