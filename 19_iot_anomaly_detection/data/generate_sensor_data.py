"""
Synthetic IoT Sensor Data Generator

Generates realistic sensor telemetry from industrial mining equipment.
50 machines across 5 remote sites, 5 sensor types, 30 days at 1-minute
intervals. Includes injected anomalies: bearing degradation (gradual drift),
sudden failures, and sensor malfunctions.

Usage:
    python generate_sensor_data.py              # Full dataset (~2.16M rows)
    python generate_sensor_data.py --sample     # Sample dataset (~50K rows)
"""

import argparse
import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta


np.random.seed(42)

SITES = ["site_alpha", "site_bravo", "site_charlie", "site_delta", "site_echo"]
MACHINES_PER_SITE = 10
SENSORS = {
    "temperature_c": {"mean": 75, "std": 5, "min": 20, "max": 150},
    "vibration_mm_s": {"mean": 2.5, "std": 0.8, "min": 0, "max": 25},
    "pressure_bar": {"mean": 6.0, "std": 0.5, "min": 0, "max": 15},
    "rpm": {"mean": 1500, "std": 100, "min": 0, "max": 3500},
    "power_kw": {"mean": 45, "std": 8, "min": 0, "max": 120},
}
EQUIPMENT_TYPES = ["excavator", "haul_truck", "drill_rig", "loader", "crusher"]


def generate_normal_readings(n_points: int, sensor_config: dict) -> np.ndarray:
    """Generate normal sensor readings with realistic patterns."""
    base = np.random.normal(sensor_config["mean"], sensor_config["std"], n_points)
    # Add daily cycle (temperature varies with shift patterns)
    hours = np.arange(n_points) / 60
    daily_cycle = sensor_config["std"] * 0.3 * np.sin(2 * np.pi * hours / 24)
    readings = base + daily_cycle
    return np.clip(readings, sensor_config["min"], sensor_config["max"])


def inject_bearing_degradation(readings: np.ndarray, start_idx: int,
                                duration: int) -> tuple[np.ndarray, list]:
    """Inject gradual drift anomaly (bearing degradation)."""
    labels = [0] * len(readings)
    drift = np.linspace(0, readings[start_idx] * 0.4, duration)
    end_idx = min(start_idx + duration, len(readings))
    actual_duration = end_idx - start_idx
    readings[start_idx:end_idx] += drift[:actual_duration]
    for i in range(start_idx, end_idx):
        labels[i] = 1
    return readings, labels


def inject_sudden_failure(readings: np.ndarray, idx: int,
                          duration: int = 30) -> tuple[np.ndarray, list]:
    """Inject sudden spike anomaly (equipment failure)."""
    labels = [0] * len(readings)
    end_idx = min(idx + duration, len(readings))
    spike_factor = np.random.uniform(2.5, 4.0)
    readings[idx:end_idx] = readings[idx] * spike_factor
    noise = np.random.normal(0, readings[idx] * 0.3, end_idx - idx)
    readings[idx:end_idx] += noise
    for i in range(idx, end_idx):
        labels[i] = 1
    return readings, labels


def inject_sensor_malfunction(readings: np.ndarray, idx: int,
                               duration: int = 60) -> tuple[np.ndarray, list]:
    """Inject sensor malfunction (flat line or erratic readings)."""
    labels = [0] * len(readings)
    end_idx = min(idx + duration, len(readings))
    if np.random.random() > 0.5:
        # Flat line
        readings[idx:end_idx] = readings[idx]
    else:
        # Erratic oscillation
        readings[idx:end_idx] = np.random.uniform(
            readings.min(), readings.max(), end_idx - idx
        )
    for i in range(idx, end_idx):
        labels[i] = 1
    return readings, labels


def generate_machine_data(machine_id: str, site: str, equip_type: str,
                          start_time: datetime, n_points: int) -> pd.DataFrame:
    """Generate full sensor data for one machine."""
    timestamps = [start_time + timedelta(minutes=i) for i in range(n_points)]

    data = {"timestamp": timestamps, "machine_id": machine_id,
            "site": site, "equipment_type": equip_type}

    all_labels = np.zeros(n_points, dtype=int)

    for sensor_name, config in SENSORS.items():
        readings = generate_normal_readings(n_points, config)

        # Randomly inject anomalies (10-15% of machines get anomalies)
        if np.random.random() < 0.15:
            anomaly_type = np.random.choice(["degradation", "failure", "malfunction"])
            anomaly_start = np.random.randint(n_points // 4, 3 * n_points // 4)

            if anomaly_type == "degradation":
                readings, labels = inject_bearing_degradation(
                    readings, anomaly_start, duration=np.random.randint(500, 2000)
                )
            elif anomaly_type == "failure":
                readings, labels = inject_sudden_failure(
                    readings, anomaly_start, duration=np.random.randint(15, 60)
                )
            else:
                readings, labels = inject_sensor_malfunction(
                    readings, anomaly_start, duration=np.random.randint(30, 120)
                )

            all_labels = np.maximum(all_labels, labels)

        data[sensor_name] = readings

    data["is_anomaly"] = all_labels
    return pd.DataFrame(data)


def generate_dataset(sample: bool = False) -> pd.DataFrame:
    """Generate the full dataset."""
    start_time = datetime(2025, 1, 1)
    n_days = 30
    n_points = n_days * 24 * 60  # 1-minute intervals

    if sample:
        # Sample: 5 machines, 7 days
        n_points = 7 * 24 * 60
        machines_per_site = 1
        sites = SITES[:5]
    else:
        machines_per_site = MACHINES_PER_SITE
        sites = SITES

    all_data = []
    machine_count = 0

    for site in sites:
        for i in range(machines_per_site):
            machine_id = f"{site}_machine_{i+1:02d}"
            equip_type = EQUIPMENT_TYPES[machine_count % len(EQUIPMENT_TYPES)]
            machine_count += 1

            df = generate_machine_data(
                machine_id, site, equip_type, start_time, n_points
            )
            all_data.append(df)
            print(f"  Generated {len(df):,} readings for {machine_id} "
                  f"({equip_type}) — anomalies: {df['is_anomaly'].sum():,}")

    dataset = pd.concat(all_data, ignore_index=True)
    return dataset


def main():
    parser = argparse.ArgumentParser(description="Generate IoT sensor data")
    parser.add_argument("--sample", action="store_true",
                       help="Generate sample dataset (~50K rows)")
    args = parser.parse_args()

    output_dir = os.path.dirname(os.path.abspath(__file__))

    print("Generating IoT sensor telemetry data...")
    print(f"Mode: {'sample' if args.sample else 'full'}")
    print("-" * 50)

    dataset = generate_dataset(sample=args.sample)

    # Save main dataset
    filename = "sensor_data_sample.csv" if args.sample else "sensor_data.csv"
    output_path = os.path.join(output_dir, filename)
    dataset.to_csv(output_path, index=False)

    # Save equipment registry
    equipment = dataset[["machine_id", "site", "equipment_type"]].drop_duplicates()
    equipment.to_csv(os.path.join(output_dir, "equipment_registry.csv"), index=False)

    print("-" * 50)
    print(f"Dataset: {len(dataset):,} rows x {len(dataset.columns)} columns")
    print(f"Machines: {dataset['machine_id'].nunique()}")
    print(f"Sites: {dataset['site'].nunique()}")
    print(f"Anomaly rate: {dataset['is_anomaly'].mean():.2%}")
    print(f"Saved to: {output_path}")
    print(f"Equipment registry: {os.path.join(output_dir, 'equipment_registry.csv')}")


if __name__ == "__main__":
    main()
