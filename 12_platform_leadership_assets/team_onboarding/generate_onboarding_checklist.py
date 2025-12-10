from dataclasses import dataclass
from typing import List
import random
import time


@dataclass
class EngineerProfile:
    """Represents a new engineer joining the team."""
    name: str
    role: str  # e.g., "Data Engineer", "Analytics Engineer"
    seniority: str  # e.g., "Junior", "Mid", "Senior", "Lead"


def generate_checklist(profile: EngineerProfile) -> List[str]:
    """Generate a personalized onboarding checklist for a new engineer.

    This demonstrates how I like to make onboarding **systematic** and
    repeatable, rather than ad-hoc.
    """
    base_tasks = [
        "Meet with manager to review expectations and goals.",
        "Get access to GitHub, CI/CD, and core data platforms.",
        "Review platform architecture and key diagrams.",
        "Complete at least one end-to-end pipeline walkthrough."
    ]

    # Role-based tasks
    if "Analytics" in profile.role:
        role_tasks = [
            "Review key BI dashboards and semantic models.",
            "Shadow an analyst to understand typical workflows.",
        ]
    else:  # Data Engineer or similar
        role_tasks = [
            "Review ingestion and transformation patterns in existing pipelines.",
            "Shadow a senior data engineer during incident triage or on-call."
        ]

    # Seniority-based tasks
    if profile.seniority in ("Senior", "Lead"):
        seniority_tasks = [
            "Review platform standards and propose at least one improvement.",
            "Lead a technical deep-dive for the team on a topic of expertise.",
        ]
    else:
        seniority_tasks = [
            "Pair with a mentor on code reviews for your first PRs.",
            "Document learnings from your first pipeline changes."
        ]

    return base_tasks + role_tasks + seniority_tasks


def pretty_print_checklist(profile: EngineerProfile, checklist: List[str]) -> str:
    """Format the checklist into a readable Markdown string."""
    lines = [
        f"# Onboarding Checklist for {profile.name}",
        "",
        f"**Role:** {profile.role}",
        f"**Seniority:** {profile.seniority}",
        "",
        "## Tasks",
    ]
    for i, task in enumerate(checklist, start=1):
        lines.append(f"{i}. {task}")
    return "\n".join(lines)


if __name__ == "__main__":
    # Example usage: this simulates generating a checklist for a senior data engineer.
    profile = EngineerProfile(
        name="New Engineer",
        role="Data Engineer",
        seniority="Senior"
    )
    checklist = generate_checklist(profile)
    md = pretty_print_checklist(profile, checklist)
    print(md)
