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
| **Data quality** | Duplicate tickets, missing values, invalid timestamps, bad equipment refs — **50 issues caught** in raw data before cleaning |
| **Python anomalies** | Recurring failures / unusual downtime — **15 assets flagged** |
| **Power BI + DAX** | Measure definitions for uptime, resolution time, SLA % (`powerbi/dax_measures.md`) |
| **Verified KPIs** | SQL/pandas outputs documented in [`docs/kpi_verification.md`](docs/kpi_verification.md) |

### Snapshot KPIs (from cleaned tables)

| KPI | Value |
|-----|------:|
| Clean service tickets | 397 |
| Avg resolution hours | 53.93 |
| SLA compliance | 52.6% |
| Total downtime hours | 2,932.6 |
| Anomalous assets | 15 |

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
    └── dashboard_spec.md
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
