-- HealthOps Intelligence — logical schema for healthcare ops analytics

CREATE TABLE equipment (
    equipment_id   VARCHAR(16) PRIMARY KEY,
    equipment_name VARCHAR(64) NOT NULL,
    equipment_type VARCHAR(32) NOT NULL,
    site           VARCHAR(64) NOT NULL,
    install_date   DATE,
    status         VARCHAR(24)
);

CREATE TABLE service_requests (
    ticket_id      VARCHAR(16) PRIMARY KEY,
    equipment_id   VARCHAR(16),
    priority       VARCHAR(16),
    status         VARCHAR(24),
    opened_at      TIMESTAMP NOT NULL,
    resolved_at    TIMESTAMP,
    sla_hours      INTEGER,
    issue_category VARCHAR(32)
);

CREATE TABLE downtime_events (
    downtime_id  VARCHAR(16) PRIMARY KEY,
    equipment_id VARCHAR(16) NOT NULL,
    started_at   TIMESTAMP NOT NULL,
    ended_at     TIMESTAMP,
    reason       VARCHAR(64)
);
