# HealthOps Intelligence

**Healthcare Operations & Quality Analytics** — completed portfolio project for equipment performance, service requests, downtime, and SLA compliance.

Built by [Veerasegaran V P](https://github.com/veera-1175).

## Live demo

**Dashboard:** [veera-1175.github.io/HealthOps-Intelligence](https://veera-1175.github.io/HealthOps-Intelligence/)

Includes KPI cards and a dashboard screenshot generated from the cleaned analytics tables.

> Dataset is **synthetic** (portfolio / interview demo). Not real patient or hospital data.

## What was delivered

| Layer | Deliverable |
|-------|-------------|
| **Synthetic ops data** | 48 equipment assets, service tickets, downtime events |
| **SQL transforms** | Schema, quality checks, reporting marts (`sql/`) |
| **Data quality** | Duplicate tickets, missing values, invalid timestamps, bad equipment refs — **50 issue instances** caught in raw data before cleaning |
| **Python anomalies** | Recurring failures / unusual downtime — **15 assets flagged** |
| **Power BI + DAX** | Measure definitions for uptime, resolution time, SLA %; KPI cards + interactive filter views (`powerbi/`, `docs/dashboard_spec.md`) |
| **Verified KPIs** | Full formulas in [`docs/kpi_verification.md`](docs/kpi_verification.md) |

### Snapshot KPIs (from cleaned tables)

| KPI | Value |
|-----|------:|
| Clean service tickets | 397 |
| Resolved tickets (SLA population) | 379 |
| Avg resolution hours (resolved) | 53.93 |
| SLA compliance (resolved tickets) | 55.1% |
| Total downtime hours | 2,932.6 |
| Anomalous assets | 15 |

## Metric definitions (interview FAQ)

### Were all 397 tickets in the SLA %?

**No.** SLA compliance uses **resolved tickets only** (`resolved_at` present) — **379** tickets.  
Open/unresolved tickets are excluded from the SLA %. Average resolution hours use the **same** resolved population.

### How are 24–96h SLA thresholds assigned?

**Ticket-level**, not priority-mapped. Each ticket has an `sla_hours` value of **24, 48, 72, or 96**.  
A ticket meets SLA when `resolution_hours <= sla_hours`. Compliance % = mean of that boolean over resolved tickets.

### What does “50 raw-data issues” count?

**Sum of issue instances** across quality checks on **raw** tables (before cleaning), from `data/processed/data_quality_report.csv`:

| Check | Issue count |
|-------|------------:|
| duplicate_service_tickets | 6 |
| missing_equipment_on_ticket | 8 |
| invalid_equipment_reference | 15 |
| missing_resolved_timestamp | 19 |
| resolved_before_opened | 0 |
| missing_downtime_end | 1 |
| downtime_end_before_start | 1 |
| invalid_downtime_equipment_ref | 0 |
| **Total** | **50** |

This is **not** “50 distinct check types” (there are 8 checks) and not “50 unique tickets” — it is the sum of flagged rows/events per rule.

### How were 15 assets flagged as anomalous?

In `src/detect_anomalies.py`, per-equipment downtime stats are computed, then:

- **Recurring failure:** `event_count` at/above the 85th percentile (and at least 3 events)
- **Unusual downtime:** `avg_downtime_hours` at/above `median + 1.5 × std`
- **Flagged** if either rule fires → **15** assets in the current run

These are heuristic review flags on synthetic data, not a clinical alerting system.

### Limitations

- Synthetic data only — planted quality issues and failure patterns for demo/interview use  
- SLA targets are ticket-level demo thresholds, not a real hospital policy by priority  
- Power BI Desktop `.pbix` is not committed (binary); DAX measures + dashboard spec + live HTML demo reproduce the KPI story  
- Anomaly thresholds are rule-based heuristics, not a trained ML model

## Project layout

```
HealthOps-Intelligence/
├── data/raw/                 # synthetic CSVs (with planted quality issues)
├── data/processed/           # cleaned tables + anomaly flags + quality report
├── sql/                      # schema, quality checks, marts
├── src/                      # generate → quality → anomalies → dashboard
├── powerbi/dax_measures.md   # DAX KPI definitions for Power BI Desktop
└── docs/
    ├── demo/                 # live dashboard (GitHub Pages)
    ├── kpi_verification.md   # verified SQL-to-dashboard KPI checks
    └── dashboard_spec.md     # pages, KPI cards, filters
```

## Reproduce

```powershell
cd HealthOps-Intelligence
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

python -m src.generate_synthetic_data
python -m src.run_quality_checks
python -m src.detect_anomalies
python -m src.build_dashboard
```

Open Power BI Desktop → get data from `data/processed/` → implement measures from `powerbi/dax_measures.md`. Card values should match `docs/kpi_verification.md` after refresh.

## Stack

Power BI · DAX · SQL · Python (pandas) · synthetic healthcare operations data

## License

MIT
