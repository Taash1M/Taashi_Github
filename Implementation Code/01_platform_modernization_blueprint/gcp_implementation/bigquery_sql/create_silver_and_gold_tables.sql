-- BigQuery SQL for Silver and Gold tables

-- Replace `your_project.your_dataset` with your project and dataset.

-- If you did not load Silver via Dataflow to BigQuery directly, you can define
-- an external table over GCS Silver here. For this example, we assume Silver
-- is already in BigQuery as `your_project.your_dataset.silver_manufacturing_events`.

-- Silver schema (example)
-- CREATE TABLE IF NOT EXISTS `your_project.your_dataset.silver_manufacturing_events` (
--   timestamp           TIMESTAMP,
--   device_id           STRING,
--   facility_id         STRING,
--   temperature_c       FLOAT64,
--   pressure_kpa        FLOAT64,
--   vibration_mm_s      FLOAT64,
--   status              STRING,
--   production_rate     INT64,
--   quality_score       FLOAT64,
--   process_date        DATE,
--   processed_timestamp TIMESTAMP
-- );


-- Gold: hourly device metrics with friendly column names and business logic
CREATE SCHEMA IF NOT EXISTS `your_project.gold_manufacturing`;

CREATE OR REPLACE TABLE `your_project.gold_manufacturing.device_metrics_hourly` AS
SELECT
  TIMESTAMP_TRUNC(timestamp, HOUR) AS hour_start,
  device_id,
  facility_id,
  COUNT(*) AS events_count,
  AVG(temperature_c) AS avg_temperature_c,
  AVG(pressure_kpa) AS avg_pressure_kpa,
  AVG(vibration_mm_s) AS avg_vibration_mm_s,
  AVG(production_rate) AS avg_units_per_hour,
  AVG(quality_score) AS avg_quality_score,
  SUM(CASE WHEN status = 'WARNING' THEN 1 ELSE 0 END) AS warning_events,
  SUM(CASE WHEN status = 'CRITICAL' THEN 1 ELSE 0 END) AS critical_events,
  CASE WHEN AVG(quality_score) >= 95.0 THEN TRUE ELSE FALSE END AS is_high_quality,
  CASE
    WHEN SUM(CASE WHEN status = 'CRITICAL' THEN 1 ELSE 0 END) > 0 THEN TRUE
    ELSE FALSE
  END AS is_high_risk
FROM `your_project.your_dataset.silver_manufacturing_events`
GROUP BY
  hour_start,
  device_id,
  facility_id;
