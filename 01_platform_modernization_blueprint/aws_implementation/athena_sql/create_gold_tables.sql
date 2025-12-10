-- Athena SQL for Silver external table and Gold CTAS

-- 1) External table over Silver data
CREATE EXTERNAL TABLE IF NOT EXISTS silver_manufacturing_events (
  timestamp                    timestamp,
  device_id                    string,
  facility_id                  string,
  temperature_c                double,
  pressure_kpa                 double,
  vibration_mm_s               double,
  status                       string,
  production_rate              int,
  quality_score                double,
  processed_timestamp          timestamp
)
PARTITIONED BY (
  process_date                 date,
  facility_id_partition        string
)
STORED AS PARQUET
LOCATION 's3://data-platform-<ACCOUNT_ID>-silver/manufacturing_events/silver/'
TBLPROPERTIES ('parquet.compression'='SNAPPY');

-- If you use partitioned folders like process_date=YYYY-MM-DD/facility_id=FAC_XXX,
-- then set up partition projection or MSCK REPAIR TABLE accordingly.
-- Example:
-- MSCK REPAIR TABLE silver_manufacturing_events;


-- 2) Gold CTAS: hourly device metrics with user-friendly columns

CREATE TABLE IF NOT EXISTS gold_device_metrics_hourly
WITH (
  format = 'PARQUET',
  external_location = 's3://data-platform-<ACCOUNT_ID>-gold/manufacturing_events/gold/',
  partitioned_by = ARRAY['date_partition']
) AS
SELECT
  date_trunc('hour', timestamp)                      AS hour_start,
  device_id                                          AS device_id,
  facility_id                                        AS facility_id,
  COUNT(*)                                           AS events_count,
  AVG(temperature_c)                                 AS avg_temperature_c,
  AVG(pressure_kpa)                                  AS avg_pressure_kpa,
  AVG(vibration_mm_s)                                AS avg_vibration_mm_s,
  AVG(production_rate)                               AS avg_units_per_hour,
  AVG(quality_score)                                 AS avg_quality_score,
  SUM(CASE WHEN status = 'WARNING' THEN 1 ELSE 0 END) AS warning_events,
  SUM(CASE WHEN status = 'CRITICAL' THEN 1 ELSE 0 END) AS critical_events,
  CASE WHEN AVG(quality_score) >= 95.0 THEN true ELSE false END AS is_high_quality,
  CASE WHEN SUM(CASE WHEN status = 'CRITICAL' THEN 1 ELSE 0 END) > 0
       THEN true ELSE false END AS is_high_risk,
  CAST(date_trunc('day', timestamp) AS date)         AS date_partition
FROM silver_manufacturing_events
GROUP BY
  date_trunc('hour', timestamp),
  device_id,
  facility_id,
  CAST(date_trunc('day', timestamp) AS date);
