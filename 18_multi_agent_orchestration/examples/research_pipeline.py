"""
Example: Multi-Agent Research Pipeline

Demonstrates agents collaborating on a research task — gathering
information from a knowledge base, synthesizing findings, and
producing a validated research report.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.orchestrator import Orchestrator


def main():
    print("=" * 60)
    print("Multi-Agent Research Pipeline")
    print("=" * 60)

    # Initialize
    orchestrator = Orchestrator(
        working_dir=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    )

    # Seed knowledge base with research documents
    docs = [
        ("ml_basics", "Machine Learning Fundamentals",
         "Supervised learning uses labeled data to train models. Common algorithms "
         "include linear regression, decision trees, and neural networks. Model "
         "evaluation uses metrics like accuracy, precision, recall, and F1 score."),
        ("llm_overview", "Large Language Model Overview",
         "LLMs are transformer-based models trained on large text corpora. They "
         "excel at text generation, summarization, and question answering. Key "
         "architectures include GPT, BERT, and T5. Fine-tuning adapts pre-trained "
         "models to specific domains."),
        ("rag_patterns", "RAG Pipeline Patterns",
         "Retrieval-Augmented Generation combines search with generation. Documents "
         "are embedded into vector space, queries retrieve relevant chunks, and an "
         "LLM generates answers grounded in the retrieved context. This reduces "
         "hallucination and enables domain-specific knowledge."),
        ("agent_arch", "Agentic AI Architecture",
         "Agentic systems use LLMs as reasoning engines that can invoke tools, "
         "maintain state, and make decisions. Key patterns include ReAct (Reason + Act), "
         "plan-and-execute, and multi-agent collaboration. Tool use follows the "
         "Model Context Protocol for standardized interfaces."),
        ("eval_methods", "AI Evaluation Methods",
         "Model evaluation goes beyond accuracy. For generation tasks, use BLEU, "
         "ROUGE, and human evaluation. For agents, measure task completion rate, "
         "tool use efficiency, and error recovery. A/B testing validates real-world "
         "impact against baselines."),
    ]

    for doc_id, title, content in docs:
        orchestrator.kb.add_document(doc_id, title, content)

    # Run research pipeline
    print("\nStarting research pipeline...")
    print("-" * 40)

    result = orchestrator.run(
        task_description="Research the current state of agentic AI systems, "
                        "focusing on multi-agent collaboration patterns, "
                        "tool use via MCP, and evaluation methods for agent pipelines.",
        task_type="research",
    )

    # Display results
    print("\n" + "=" * 60)
    print("RESEARCH RESULTS")
    print("=" * 60)
    print(f"Success: {result['success']}")
    print(f"Duration: {result['duration_seconds']}s")
    print(f"Stages completed: {len(result['stages'])}")

    for stage in result["stages"]:
        stage_name = stage["stage"].upper()
        stage_result = stage.get("result", {})
        if isinstance(stage_result, dict):
            if stage_name == "RESEARCH":
                n_results = len(stage_result.get("search_results", []))
                print(f"\n  [{stage_name}] Found {n_results} relevant documents")
                for sr in stage_result.get("search_results", [])[:3]:
                    print(f"    - {sr.get('title', sr.get('doc_id', 'unknown'))} "
                          f"(score: {sr.get('score', 'N/A')})")
            elif stage_name == "REVIEW":
                print(f"\n  [{stage_name}] {stage_result.get('recommendation', 'N/A')}")
                print(f"    Score: {stage_result.get('score', 'N/A')}")

    return result


if __name__ == "__main__":
    main()
