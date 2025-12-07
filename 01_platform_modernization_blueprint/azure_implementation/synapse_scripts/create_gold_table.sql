-- Synapse Gold table for manufacturing device hourly metrics

CREATE DATABASE IF NOT EXISTS gold_manufacturing;
GO

USE gold_manufacturing;
GO

IF OBJECT_ID('dbo.fact_device_metrics_hourly', 'U') IS NOT NULL
    DROP TABLE dbo.fact_device_metrics_hourly;
GO

CREATE TABLE dbo.fact_device_metrics_hourly
(
    metric_id BIGINT IDENTITY(1,1) PRIMARY KEY,
    hour_start DATETIME2 NOT NULL,
    device_id NVARCHAR(50) NOT NULL,
    facility_id NVARCHAR(50) NOT NULL,
    events_count INT,
    avg_temperature_c DECIMAL(10,2),
    avg_pressure_kpa DECIMAL(10,2),
    avg_vibration_mm_s DECIMAL(10,2),
    avg_units_per_hour DECIMAL(10,2),
    avg_quality_score DECIMAL(10,2),
    warning_events INT,
    critical_events INT,
    is_high_quality BIT,
    is_high_risk BIT,
    created_at DATETIME2 DEFAULT SYSUTCDATETIME()
)
WITH
(
    DISTRIBUTION = HASH(device_id),
    CLUSTERED COLUMNSTORE INDEX
);
GO

-- Example query to read from Delta in ADLS and populate the table.
-- Replace <STORAGE_ACCOUNT> with your actual storage account name.
TRUNCATE TABLE dbo.fact_device_metrics_hourly;
GO

INSERT INTO dbo.fact_device_metrics_hourly
(
    hour_start,
    device_id,
    facility_id,
    events_count,
    avg_temperature_c,
    avg_pressure_kpa,
    avg_vibration_mm_s,
    avg_units_per_hour,
    avg_quality_score,
    warning_events,
    critical_events,
    is_high_quality,
    is_high_risk
)
SELECT
    hour_start,
    device_id,
    facility_id,
    events_count,
    avg_temperature_c,
    avg_pressure_kpa,
    avg_vibration_mm_s,
    avg_units_per_hour,
    avg_quality_score,
    warning_events,
    critical_events,
    CAST(is_high_quality AS BIT) AS is_high_quality,
    CAST(is_high_risk AS BIT) AS is_high_risk
FROM
    OPENROWSET(
        BULK 'https://<STORAGE_ACCOUNT>.dfs.core.windows.net/gold/manufacturing_events/gold/',
        FORMAT = 'DELTA'
    ) AS gold_data;
GO
