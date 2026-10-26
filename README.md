# HealthOps Intelligence

**Healthcare Operations & Quality Analytics** — interactive Power BI platform for equipment performance, service requests, downtime, and SLA compliance.

Built by [Veerasegaran V P](https://github.com/veera-1175).

## What it does

| Layer | Purpose |
|-------|---------|
| **Synthetic ops data** | Equipment, service tickets, downtime events, and SLA targets modeled on healthcare equipment workflows |
| **SQL transforms** | Cleaning + data-quality checks (duplicates, missing values, invalid timestamps, bad equipment refs) |
| **Python anomalies** | Flags unusual downtime patterns and recurring equipment failures |
| **Power BI + DAX** | Interactive dashboards and KPI measures for uptime, resolution time, and SLA performance |

> Dataset is **synthetic** (generated for portfolio / interview demos). It is not real patient or hospital data.

## Project layout

```
HealthOps-Intelligence/
├── data/
│   ├── raw/                 # generated synthetic CSVs
│   └── processed/           # cleaned tables + anomaly flags
├── sql/
│   ├── 01_schema.sql
│   ├── 02_quality_checks.sql
│   └── 03_marts.sql
├── src/
│   ├── generate_synthetic_data.py
│   ├── run_quality_checks.py
│   └── detect_anomalies.py
├── powerbi/
│   └── dax_measures.md      # validated DAX KPI definitions
└── docs/
    └── dashboard_spec.md    # Power BI page & visual map
```

## Quick start

```powershell
cd HealthOps-Intelligence
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

python -m src.generate_synthetic_data
python -m src.run_quality_checks
python -m src.detect_anomalies
```

Then connect Power BI Desktop to `data/processed/` (CSV / folder) and implement the measures in `powerbi/dax_measures.md`.

## KPI focus

- **Equipment uptime %**
- **Mean / median service resolution time**
- **SLA compliance %** (on-time vs breached)
- **Downtime hours by equipment / site**
- **Recurring failure rate** (anomaly-assisted)

## Stack

Power BI · DAX · SQL · Python (pandas) · synthetic healthcare operations data

## License

MIT
