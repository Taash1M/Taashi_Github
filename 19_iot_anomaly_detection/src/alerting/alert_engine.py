"""
Alert Engine — Threshold + ML-based alert routing.

Combines model anomaly scores with configurable rule-based thresholds
to generate, classify, and route alerts. Supports severity levels,
cooldown periods, and alert aggregation.
"""

import time
import yaml
import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class Alert:
    """A generated alert."""
    alert_id: str
    machine_id: str
    site: str
    severity: AlertSeverity
    message: str
    anomaly_score: float
    sensor_values: dict = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "alert_id": self.alert_id,
            "machine_id": self.machine_id,
            "site": self.site,
            "severity": self.severity.value,
            "message": self.message,
            "anomaly_score": round(self.anomaly_score, 4),
            "sensor_values": self.sensor_values,
            "timestamp": self.timestamp,
        }


class AlertEngine:
    """
    Alert generation and routing engine.

    Rules:
    - score >= 0.9: CRITICAL
    - score >= 0.7: WARNING
    - score >= 0.5: INFO
    - Cooldown: no duplicate alerts for same machine within N minutes
    """

    def __init__(self, config_path: str | None = None):
        self._alerts: list[Alert] = []
        self._last_alert_time: dict[str, float] = {}
        self._alert_counter = 0

        # Default thresholds
        self.thresholds = {
            "critical": 0.9,
            "warning": 0.7,
            "info": 0.5,
        }
        self.cooldown_minutes = 15

        if config_path and os.path.exists(config_path):
            self._load_config(config_path)

    def _load_config(self, path: str) -> None:
        with open(path) as f:
            config = yaml.safe_load(f)
        self.thresholds = config.get("thresholds", self.thresholds)
        self.cooldown_minutes = config.get("cooldown_minutes", self.cooldown_minutes)

    def _in_cooldown(self, machine_id: str) -> bool:
        last = self._last_alert_time.get(machine_id, 0)
        return (time.time() - last) < (self.cooldown_minutes * 60)

    def _classify_severity(self, score: float) -> AlertSeverity | None:
        if score >= self.thresholds["critical"]:
            return AlertSeverity.CRITICAL
        elif score >= self.thresholds["warning"]:
            return AlertSeverity.WARNING
        elif score >= self.thresholds["info"]:
            return AlertSeverity.INFO
        return None

    def evaluate(self, machine_id: str, site: str,
                 anomaly_score: float,
                 sensor_values: dict | None = None) -> Alert | None:
        """
        Evaluate an anomaly score and generate an alert if warranted.

        Returns an Alert if the score exceeds thresholds and the
        machine is not in cooldown. Returns None otherwise.
        """
        severity = self._classify_severity(anomaly_score)
        if severity is None:
            return None

        if self._in_cooldown(machine_id) and severity != AlertSeverity.CRITICAL:
            return None

        self._alert_counter += 1
        alert_id = f"ALT-{self._alert_counter:06d}"

        messages = {
            AlertSeverity.CRITICAL: f"CRITICAL anomaly detected on {machine_id} at {site}",
            AlertSeverity.WARNING: f"Elevated anomaly score on {machine_id} at {site}",
            AlertSeverity.INFO: f"Minor anomaly detected on {machine_id} at {site}",
        }

        alert = Alert(
            alert_id=alert_id,
            machine_id=machine_id,
            site=site,
            severity=severity,
            message=messages[severity],
            anomaly_score=anomaly_score,
            sensor_values=sensor_values or {},
        )

        self._alerts.append(alert)
        self._last_alert_time[machine_id] = time.time()
        return alert

    def get_alerts(self, severity: str | None = None,
                   site: str | None = None,
                   limit: int = 50) -> list[dict]:
        """Query alerts with optional filters."""
        alerts = self._alerts
        if severity:
            alerts = [a for a in alerts if a.severity.value == severity]
        if site:
            alerts = [a for a in alerts if a.site == site]
        return [a.to_dict() for a in alerts[-limit:]]

    def summary(self) -> dict:
        """Get alert summary statistics."""
        by_severity = {}
        for sev in AlertSeverity:
            count = sum(1 for a in self._alerts if a.severity == sev)
            by_severity[sev.value] = count

        by_site = {}
        for alert in self._alerts:
            by_site[alert.site] = by_site.get(alert.site, 0) + 1

        return {
            "total_alerts": len(self._alerts),
            "by_severity": by_severity,
            "by_site": by_site,
            "machines_alerting": len(set(a.machine_id for a in self._alerts)),
        }
