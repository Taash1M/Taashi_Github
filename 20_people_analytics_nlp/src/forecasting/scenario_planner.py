"""
What-If Scenario Modeling for Workforce Planning

Allows HR leaders to model scenarios:
- "What if attrition increases by 20%?"
- "What if we freeze hiring in Q3?"
- "What if Engineering grows 50% next year?"
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class Scenario:
    """Definition of a what-if scenario."""
    name: str
    description: str
    parameters: dict  # e.g., {"attrition_multiplier": 1.2, "hiring_freeze": True}


@dataclass
class ScenarioResult:
    """Result of running a scenario simulation."""
    scenario_name: str
    baseline_headcount: dict[str, int]
    projected_headcount: dict[str, int]
    net_change: dict[str, int]
    total_baseline: int
    total_projected: int
    months_simulated: int


class ScenarioPlanner:
    """
    Simulate workforce planning scenarios on headcount data.

    Uses historical hiring/attrition rates as a baseline, then applies
    scenario-specific modifiers to project future headcount.
    """

    PRESET_SCENARIOS = {
        "attrition_spike": Scenario(
            name="Attrition Spike (+20%)",
            description="Attrition rate increases by 20% across all departments",
            parameters={"attrition_multiplier": 1.2}
        ),
        "hiring_freeze": Scenario(
            name="Hiring Freeze (Q3-Q4)",
            description="All hiring paused for 6 months",
            parameters={"hiring_multiplier": 0.0, "freeze_months": 6}
        ),
        "rapid_growth": Scenario(
            name="Rapid Growth (+50% Engineering)",
            description="Engineering department grows 50% over 12 months",
            parameters={"dept_growth": {"Engineering": 1.5}}
        ),
        "recession": Scenario(
            name="Economic Downturn",
            description="10% RIF + hiring freeze for 9 months",
            parameters={
                "rif_pct": 0.10,
                "hiring_multiplier": 0.0,
                "freeze_months": 9,
            }
        ),
    }

    def __init__(self, simulation_months: int = 12):
        self.simulation_months = simulation_months

    def compute_baseline_rates(self, headcount_df: pd.DataFrame) -> dict:
        """Compute average monthly hire and departure rates per department."""
        rates = {}
        for dept in headcount_df["department"].unique():
            dept_data = headcount_df[headcount_df["department"] == dept].sort_values("date")
            if len(dept_data) < 3:
                continue

            avg_headcount = dept_data["headcount"].mean()
            avg_hires = dept_data["hires"].mean()
            avg_departures = dept_data["departures"].mean()

            rates[dept] = {
                "current_headcount": int(dept_data["headcount"].iloc[-1]),
                "avg_monthly_hires": round(avg_hires, 2),
                "avg_monthly_departures": round(avg_departures, 2),
                "hire_rate": round(avg_hires / avg_headcount, 4) if avg_headcount > 0 else 0,
                "departure_rate": round(avg_departures / avg_headcount, 4) if avg_headcount > 0 else 0,
            }

        return rates

    def simulate(self, headcount_df: pd.DataFrame,
                 scenario: Scenario) -> ScenarioResult:
        """Run a scenario simulation."""
        rates = self.compute_baseline_rates(headcount_df)
        params = scenario.parameters

        baseline = {}
        projected = {}

        for dept, dept_rates in rates.items():
            hc = dept_rates["current_headcount"]
            baseline[dept] = hc

            # Apply RIF if specified
            if "rif_pct" in params:
                hc = int(hc * (1 - params["rif_pct"]))

            # Simulate month by month
            for month in range(self.simulation_months):
                # Hiring
                hire_rate = dept_rates["hire_rate"]
                if "hiring_multiplier" in params:
                    freeze_months = params.get("freeze_months", self.simulation_months)
                    if month < freeze_months:
                        hire_rate *= params["hiring_multiplier"]

                if "dept_growth" in params and dept in params["dept_growth"]:
                    # Distribute growth evenly across months
                    growth_factor = params["dept_growth"][dept]
                    target = baseline[dept] * growth_factor
                    monthly_extra = (target - baseline[dept]) / self.simulation_months
                    hires = max(0, int(hire_rate * hc + monthly_extra))
                else:
                    hires = max(0, int(hire_rate * hc))

                # Departures
                depart_rate = dept_rates["departure_rate"]
                if "attrition_multiplier" in params:
                    depart_rate *= params["attrition_multiplier"]

                departures = max(0, int(depart_rate * hc))
                hc = max(1, hc + hires - departures)

            projected[dept] = hc

        net_change = {dept: projected[dept] - baseline[dept] for dept in baseline}

        return ScenarioResult(
            scenario_name=scenario.name,
            baseline_headcount=baseline,
            projected_headcount=projected,
            net_change=net_change,
            total_baseline=sum(baseline.values()),
            total_projected=sum(projected.values()),
            months_simulated=self.simulation_months,
        )

    def compare_scenarios(self, headcount_df: pd.DataFrame,
                          scenarios: list[Scenario] = None) -> pd.DataFrame:
        """Run multiple scenarios and compare results."""
        if scenarios is None:
            scenarios = list(self.PRESET_SCENARIOS.values())

        records = []
        for scenario in scenarios:
            result = self.simulate(headcount_df, scenario)
            records.append({
                "scenario": result.scenario_name,
                "baseline_total": result.total_baseline,
                "projected_total": result.total_projected,
                "net_change": result.total_projected - result.total_baseline,
                "pct_change": round(
                    (result.total_projected - result.total_baseline) / result.total_baseline * 100, 1
                ) if result.total_baseline > 0 else 0,
                "months": result.months_simulated,
            })

        return pd.DataFrame(records).sort_values("net_change")

    def department_impact(self, headcount_df: pd.DataFrame,
                          scenario: Scenario) -> pd.DataFrame:
        """Show per-department impact of a scenario."""
        result = self.simulate(headcount_df, scenario)

        records = []
        for dept in result.baseline_headcount:
            base = result.baseline_headcount[dept]
            proj = result.projected_headcount[dept]
            records.append({
                "department": dept,
                "baseline": base,
                "projected": proj,
                "net_change": proj - base,
                "pct_change": round((proj - base) / base * 100, 1) if base > 0 else 0,
            })

        return pd.DataFrame(records).sort_values("net_change")
