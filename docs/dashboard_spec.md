# Power BI dashboard spec — HealthOps Intelligence

## Page 1 — Operations overview

- KPI row: Equipment Uptime %, SLA Compliance %, Avg Resolution Hours, Open Tickets  
- Downtime hours by site (bar)  
- Ticket volume trend (line)  
- Priority mix (donut)

## Page 2 — Equipment performance

- Uptime by equipment type  
- Top 10 assets by downtime hours  
- Service requests by issue category  
- Filter pane: site, equipment type, date range

## Page 3 — Quality & anomalies

- Data quality issue counts (from `data_quality_report.csv`)  
- Anomalous assets table (recurring failures / unusual downtime)  
- SLA breach detail table for Critical / High priority

## Data sources

Folder: `data/processed/`

- `equipment.csv`  
- `service_requests.csv`  
- `downtime_events.csv`  
- `equipment_anomaly_flags.csv`  
- `data_quality_report.csv`  
