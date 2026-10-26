# SQL → analytics KPI verification

These KPIs are computed from the cleaned tables in `data/processed/` (same grain Power BI should use after SQL/pandas transforms).

## Verified KPI values

| KPI | Value | Source logic |
|-----|------:|--------------|
| Equipment assets | 48 | `COUNT(*)` on equipment |
| Service tickets (clean) | 397 | de-duplicated + valid equipment refs |
| Resolved tickets | 379 | `resolved_at IS NOT NULL` |
| Avg resolution hours | 53.93 | `AVG(resolution_hours)` on resolved tickets |
| SLA compliance % | 55.1% | resolved tickets with `resolution_hours <= sla_hours` |
| Total downtime hours | 2932.6 | `SUM(downtime_hours)` |
| Anomalous assets | 15 | Python anomaly flags |
| Raw quality issues caught | 50 | sum of quality check counts |

## SLA definition (interview-ready)

- **Eligible population:** resolved tickets only (`resolved_at` is present).
- **SLA threshold:** each ticket has its own target in `sla_hours` — one of **24, 48, 72, or 96** hours.
- **Calculation:** `sla_met = resolution_hours <= sla_hours`; compliance % = mean of `sla_met` over resolved tickets.
- **Avg resolution hours:** mean `resolution_hours` over the same resolved population (can exceed the modal SLA target when many tickets breach).

## Raw data-quality checks (before cleaning)

| Check | Issues |
|-------|-------:|
| duplicate_service_tickets | 6 |
| missing_equipment_on_ticket | 8 |
| invalid_equipment_reference | 15 |
| missing_resolved_timestamp | 19 |
| resolved_before_opened | 0 |
| missing_downtime_end | 1 |
| downtime_end_before_start | 1 |
| invalid_downtime_equipment_ref | 0 |

## Power BI alignment

Implement the DAX measures in `powerbi/dax_measures.md` against these processed tables. Card values for SLA %, average resolution hours, total downtime, and anomalous assets should match this verification file after refresh.
