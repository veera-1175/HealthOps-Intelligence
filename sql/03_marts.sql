-- Reporting marts consumed by Power BI

-- Ticket fact with SLA outcome
CREATE VIEW fact_service_requests AS
SELECT
    ticket_id,
    equipment_id,
    priority,
    status,
    opened_at,
    resolved_at,
    sla_hours,
    issue_category,
    EXTRACT(EPOCH FROM (resolved_at - opened_at)) / 3600.0 AS resolution_hours,
    CASE
        WHEN resolved_at IS NULL THEN NULL
        WHEN EXTRACT(EPOCH FROM (resolved_at - opened_at)) / 3600.0 <= sla_hours THEN TRUE
        ELSE FALSE
    END AS sla_met
FROM service_requests;

-- Downtime fact
CREATE VIEW fact_downtime AS
SELECT
    downtime_id,
    equipment_id,
    started_at,
    ended_at,
    reason,
    EXTRACT(EPOCH FROM (ended_at - started_at)) / 3600.0 AS downtime_hours
FROM downtime_events
WHERE ended_at IS NOT NULL
  AND ended_at >= started_at;

-- Equipment uptime proxy by site (illustrative calendar window)
-- Replace :window_hours with the reporting period length in hours.
CREATE VIEW mart_equipment_kpis AS
SELECT
    e.equipment_id,
    e.equipment_name,
    e.equipment_type,
    e.site,
    COALESCE(SUM(d.downtime_hours), 0) AS total_downtime_hours,
    COUNT(d.downtime_id) AS downtime_events
FROM equipment e
LEFT JOIN fact_downtime d ON e.equipment_id = d.equipment_id
GROUP BY e.equipment_id, e.equipment_name, e.equipment_type, e.site;
