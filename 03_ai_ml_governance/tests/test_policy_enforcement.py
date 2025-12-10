import pytest
from src.pipeline import run_summarization_pipeline, FakeLLM, load_governance_config

def test_policy_tag_required():
    cfg = load_governance_config()
    llm = FakeLLM("gpt-4o-mini", cfg)
    with pytest.raises(ValueError):
        llm.summarize("test text", policy_tag=None)

def test_allowed_model():
    cfg = load_governance_config()
    _ = FakeLLM("gpt-4", cfg)  # should not raise
    with pytest.raises(ValueError):
        FakeLLM("some-unknown-model", cfg)

def test_summarization_pipeline():
    out = run_summarization_pipeline("hello world", policy_tag="internal_use_only")
    assert "SUMMARY" in out
    assert "policy=internal_use_only" in out
