# HealthOps Intelligence — validated DAX measures

Use these measures after loading `data/processed/*.csv` into Power BI and creating relationships:

- `equipment[equipment_id] 1—* service_requests[equipment_id]`
- `equipment[equipment_id] 1—* downtime_events[equipment_id]`
- `equipment[equipment_id] 1—* equipment_anomaly_flags[equipment_id]`

Assume a reporting period parameter or fixed window (e.g. 2160 hours ≈ 90 days) named `Reporting Hours`.

## Core KPIs

```dax
Total Tickets =
COUNTROWS ( 'service_requests' )
```

```dax
Resolved Tickets =
CALCULATE (
    COUNTROWS ( 'service_requests' ),
    NOT ISBLANK ( 'service_requests'[resolved_at] )
)
```

```dax
Avg Resolution Hours =
AVERAGE ( 'service_requests'[resolution_hours] )
```

```dax
SLA Compliance % =
DIVIDE (
    CALCULATE (
        COUNTROWS ( 'service_requests' ),
        'service_requests'[sla_met] = TRUE ()
    ),
    CALCULATE (
        COUNTROWS ( 'service_requests' ),
        NOT ISBLANK ( 'service_requests'[sla_met] )
    )
)
```

```dax
Total Downtime Hours =
SUM ( 'downtime_events'[downtime_hours] )
```

```dax
Equipment Uptime % =
VAR WindowHours = 2160
RETURN
DIVIDE ( WindowHours - [Total Downtime Hours], WindowHours )
```

```dax
Anomalous Assets =
CALCULATE (
    DISTINCTCOUNT ( 'equipment_anomaly_flags'[equipment_id] ),
    'equipment_anomaly_flags'[anomaly_flag] = TRUE ()
)
```

## Suggested visuals

1. KPI cards: Uptime %, SLA Compliance %, Avg Resolution Hours, Anomalous Assets  
2. Bar: downtime hours by equipment type / site  
3. Line: tickets opened vs resolved by week  
4. Table: anomalous equipment with reason flags  
5. Matrix: SLA met vs breached by priority  
