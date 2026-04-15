"""
Automated Model Card Generation

Generates model cards following Google's Model Card framework,
adapted for HR analytics models. Includes intended use, metrics,
ethical considerations, and fairness results.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime

import pandas as pd


@dataclass
class ModelCard:
    """Structured model card for an HR prediction model."""
    model_name: str
    model_version: str
    model_type: str
    description: str
    intended_use: str
    out_of_scope_uses: list[str]
    training_data_description: str
    evaluation_metrics: dict[str, float]
    fairness_results: dict[str, dict]
    ethical_considerations: list[str]
    limitations: list[str]
    created_date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    owner: str = "People Analytics Team"
    status: str = "Draft"


class ModelCardGenerator:
    """
    Generate model cards for HR analytics models.

    Model cards provide transparency about:
    - What the model does and doesn't do
    - How it was trained and evaluated
    - Known fairness issues and limitations
    - Ethical considerations for HR use cases
    """

    HR_ETHICAL_CONSIDERATIONS = [
        "Model predictions should not be the sole basis for employment decisions",
        "Human review is required before any adverse action based on model output",
        "Protected attributes must not be used as model features in production",
        "Regular bias audits required on a quarterly basis",
        "Model retraining required when population demographics shift significantly",
        "Candidates/employees have the right to explanation of decisions affecting them",
    ]

    HR_LIMITATIONS = [
        "Model accuracy may degrade for underrepresented demographic groups",
        "Historical data may encode past biases that the model could perpetuate",
        "Performance metrics computed on training distribution may not reflect deployment",
        "Model does not account for external economic factors or market conditions",
    ]

    def generate(self, model_name: str, model_version: str,
                 model_type: str, description: str,
                 intended_use: str,
                 metrics: dict[str, float],
                 fairness_results: dict = None) -> ModelCard:
        """Generate a model card."""
        out_of_scope = [
            "Automated decision-making without human oversight",
            "Predictions on populations significantly different from training data",
            "Use as a screening tool that replaces human judgment entirely",
        ]

        return ModelCard(
            model_name=model_name,
            model_version=model_version,
            model_type=model_type,
            description=description,
            intended_use=intended_use,
            out_of_scope_uses=out_of_scope,
            training_data_description=f"Synthetic HR data ({model_type} predictions)",
            evaluation_metrics=metrics,
            fairness_results=fairness_results or {},
            ethical_considerations=self.HR_ETHICAL_CONSIDERATIONS.copy(),
            limitations=self.HR_LIMITATIONS.copy(),
        )

    def to_markdown(self, card: ModelCard) -> str:
        """Render model card as markdown."""
        lines = [
            f"# Model Card: {card.model_name}",
            "",
            f"**Version:** {card.model_version}  ",
            f"**Type:** {card.model_type}  ",
            f"**Owner:** {card.owner}  ",
            f"**Status:** {card.status}  ",
            f"**Date:** {card.created_date}",
            "",
            "## Description",
            card.description,
            "",
            "## Intended Use",
            card.intended_use,
            "",
            "## Out of Scope Uses",
        ]
        for use in card.out_of_scope_uses:
            lines.append(f"- {use}")

        lines += [
            "",
            "## Training Data",
            card.training_data_description,
            "",
            "## Evaluation Metrics",
            "",
            "| Metric | Value |",
            "|--------|-------|",
        ]
        for metric, value in card.evaluation_metrics.items():
            lines.append(f"| {metric} | {value} |")

        if card.fairness_results:
            lines += ["", "## Fairness Results", ""]
            for attr, results in card.fairness_results.items():
                lines.append(f"### {attr}")
                for k, v in results.items():
                    lines.append(f"- **{k}:** {v}")
                lines.append("")

        lines += ["", "## Ethical Considerations", ""]
        for item in card.ethical_considerations:
            lines.append(f"- {item}")

        lines += ["", "## Limitations", ""]
        for item in card.limitations:
            lines.append(f"- {item}")

        return "\n".join(lines)

    def to_dict(self, card: ModelCard) -> dict:
        """Convert model card to dictionary."""
        return {
            "model_name": card.model_name,
            "model_version": card.model_version,
            "model_type": card.model_type,
            "description": card.description,
            "intended_use": card.intended_use,
            "out_of_scope_uses": card.out_of_scope_uses,
            "training_data": card.training_data_description,
            "metrics": card.evaluation_metrics,
            "fairness": card.fairness_results,
            "ethical_considerations": card.ethical_considerations,
            "limitations": card.limitations,
            "owner": card.owner,
            "status": card.status,
            "date": card.created_date,
        }
