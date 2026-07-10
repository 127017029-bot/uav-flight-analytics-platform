-- ====================================================================
-- AI-Powered UAV Digital Twin & Predictive Maintenance Platform
-- TimescaleDB Hypertable Migration Script
-- ====================================================================
-- This migration script transitions the high-frequency telemetry table 
-- into a TimescaleDB Hypertable partitioned by time.
-- Run this on your production PostgreSQL instance after applying Django migrations.

-- 1. Enable TimescaleDB Extension
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- 2. Drop constraints that interfere with partitioning (if applicable)
-- TimescaleDB requires primary keys to include the partitioning column (timestamp).
ALTER TABLE telemetry_telemetrydata DROP CONSTRAINT IF EXISTS telemetry_telemetrydata_pkey;

-- 3. Create a composite Primary Key including timestamp
ALTER TABLE telemetry_telemetrydata ADD PRIMARY KEY (id, timestamp);

-- 4. Convert telemetry data table to TimescaleDB Hypertable
-- Partitions data automatically in 7-day intervals based on time.
SELECT create_hypertable('telemetry_telemetrydata', 'timestamp', chunk_time_interval => INTERVAL '7 days', if_not_exists => TRUE);

-- 5. Build optimized composite indexes for real-time querying & sorting
CREATE INDEX IF NOT EXISTS telemetry_drone_time_idx ON telemetry_telemetrydata (flight_id, timestamp DESC);

-- 6. Setup TimescaleDB Data Retention Policy
-- Automatically drops telemetry data chunks older than 90 days to conserve space
SELECT add_retention_policy('telemetry_telemetrydata', INTERVAL '90 days', if_not_exists => TRUE);

-- 7. Setup Compression Policy
-- Compresses old chunks older than 14 days to achieve ~90% storage savings
ALTER TABLE telemetry_telemetrydata SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'flight_id',
    timescaledb.compress_orderby = 'timestamp DESC'
);

SELECT add_compression_policy('telemetry_telemetrydata', INTERVAL '14 days', if_not_exists => TRUE);
