# mcp_client.py
# This script simulates a secure, governed client for an LLM service, demonstrating
# the kind of production-grade AI integration and governance a Director of Data Engineering
# would oversee.

import json
import time
from typing import Dict, Any

# --- Configuration ---
GOVERNANCE_CONFIG_PATH = "governance_config.json"

def load_governance_config() -> Dict[str, Any]:
    """Loads governance rules from a conceptual configuration file."""
    try:
        with open(GOVERNANCE_CONFIG_PATH, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Default configuration for demonstration
        return {
            "rate_limit_per_minute": 60,
            "max_tokens_per_request": 4096,
            "allowed_models": ["gpt-4.1-mini", "gemini-2.5-flash"],
            "cost_threshold_usd": 100.00
        }

def mask_data(prompt: str) -> str:
    """Simulates PII masking logic before sending to external LLM."""
    # Conceptual masking: replace common PII patterns
    masked_prompt = prompt.replace("Social Security Number", "[MASKED_SSN]")
    masked_prompt = masked_prompt.replace("taashir@gmail.com", "[MASKED_EMAIL]")
    return masked_prompt

def call_llm_service(prompt: str, model: str) -> str:
    """
    Simulates a call to the LLM service, governed by the MCP.
    """
    config = load_governance_config()
    
    # 1. Governance Check: Model
    if model not in config["allowed_models"]:
        raise ValueError(f"Model '{model}' is not on the allowed list for production use.")
        
    # 2. Security Check: Masking
    start_time = time.time()
    governed_prompt = mask_data(prompt)
    
    # 3. Rate Limiting (Conceptual)
    # In a real system, this would check a Redis counter
    
    # 4. Simulated API Call
    print(f"Sending governed prompt to {model}...")
    print(f"Original: '{prompt[:30]}...'")
    print(f"Governed: '{governed_prompt[:30]}...'")
    time.sleep(0.5) # Simulate network latency
    
    # 5. Observability: Logging
    latency = time.time() - start_time
    print(f"MCP Log: model={model}, latency={latency:.2f}s, tokens_used=500")
    
    # 6. Simulated Response
    return f"LLM Response: Analysis complete based on governed input. Latency: {latency:.2f}s."

if __name__ == "__main__":
    # Create the governance config file
    with open(GOVERNANCE_CONFIG_PATH, 'w') as f:
        json.dump(load_governance_config(), f, indent=4)
        
    # Example of a successful, governed call
    try:
        response = call_llm_service(
            prompt="Analyze the sentiment of customer feedback regarding the new platform migration.",
            model="gpt-4.1-mini"
        )
        print("\n--- Result ---")
        print(response)
    except Exception as e:
        print(f"Error during LLM call: {e}")
        
    # Example of a governance failure (unauthorized model)
    try:
        call_llm_service(
            prompt="Generate a new marketing slogan.",
            model="unauthorized-model-v1"
        )
    except ValueError as e:
        print(f"\n--- Governance Failure ---")
        print(f"Caught expected error: {e}")
