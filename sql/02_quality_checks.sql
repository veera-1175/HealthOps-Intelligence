-- Data-quality checks (run against raw / staging tables)

-- 1) Duplicate service tickets
SELECT ticket_id, COUNT(*) AS dup_count
FROM service_requests
GROUP BY ticket_id
HAVING COUNT(*) > 1;

-- 2) Missing equipment on tickets
SELECT *
FROM service_requests
WHERE equipment_id IS NULL OR TRIM(equipment_id) = '';

-- 3) Invalid equipment references
SELECT sr.*
FROM service_requests sr
LEFT JOIN equipment e ON sr.equipment_id = e.equipment_id
WHERE sr.equipment_id IS NOT NULL
  AND e.equipment_id IS NULL;

-- 4) Missing / invalid timestamps
SELECT *
FROM service_requests
WHERE resolved_at IS NOT NULL
  AND resolved_at < opened_at;

SELECT *
FROM downtime_events
WHERE ended_at IS NOT NULL
  AND ended_at < started_at;

-- 5) Missing downtime end times
SELECT *
FROM downtime_events
WHERE ended_at IS NULL;
