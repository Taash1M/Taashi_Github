from dataclasses import dataclass
from typing import List, Dict
import pytest

@dataclass
class GovernanceConfig:
    allowed_models: List[str]
    max_tokens: int
    require_policy_tag: bool

class FakeLLM:
    def __init__(self, model_name: str, config: GovernanceConfig):
        if model_name not in config.allowed_models:
            raise ValueError(f"Model {model_name} is not allowed by governance policy.")
        self.model_name = model_name
        self.config = config

    def summarize(self, text: str, policy_tag: str | None = None) -> str:
        if self.config.require_policy_tag and not policy_tag:
            raise ValueError("Policy tag is required by governance.")
        snippet = text[:200]
        return f"[SUMMARY by {self.model_name} | policy={policy_tag}] {snippet}"

def load_governance_config() -> GovernanceConfig:
    # In real life, load from YAML. Here we hard-code for demo.
    return GovernanceConfig(
        allowed_models=["gpt-4", "gpt-4o-mini"],
        max_tokens=2048,
        require_policy_tag=True,
    )

def run_summarization_pipeline(text: str, policy_tag: str) -> str:
    cfg = load_governance_config()
    llm = FakeLLM("gpt-4o-mini", cfg)
    return llm.summarize(text, policy_tag=policy_tag)

if __name__ == "__main__":
    demo_text = "This is a sample input document that would be summarized under a governed pipeline..."
    print(run_summarization_pipeline(demo_text, policy_tag="public_marketing"))
