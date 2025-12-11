import os

def update_root_readme():
    readme_path = "/workspaces/Taashi_Github/README.md"
    
    # The content to insert
    ai_section = """
---
## 🧠 Section 3: AI & Agentic Architectures

### Project 16: The Wall Street Swarm (Multi-Agent Financial System)
* **Goal:** Automate high-value investment research by mimicking a human analyst team (Researcher + Quant + Writer).
* **Architecture:** **Agentic Workflow** using sequential hand-offs and deterministic tool use.
* **Key Tech:** Python, LLM Orchestration, Vector Search Patterns.
* **Why it Matters:** Demonstrates how to solve **hallucination** and **auditability** challenges in FinTech by decoupling "Reasoning" (LLM) from "Knowledge" (Deterministic Tools).
* **[View Project Code](./Implementation%20Code/16_Agentic_Financial_Analyst)**

"""

    print(f"📖 Reading: {readme_path}")
    
    try:
        with open(readme_path, "r") as f:
            content = f.read()

        # TARGET: We want to insert BEFORE "Technical Leadership"
        # We assume the header looks something like "## Technical Leadership" or similar.
        target_marker = "Technical Leadership"
        
        # Find where the Technical Leadership section starts
        insert_index = content.find(target_marker)

        if insert_index != -1:
            # We found the target!
            # We need to find the specific '#' before "Technical Leadership" to insert cleanly before the header
            # Scan backwards from the text match to find the start of that line
            line_start = content.rfind('\n', 0, insert_index)
            
            # Split the file into two parts
            part_1 = content[:line_start]  # Everything before Technical Leadership
            part_2 = content[line_start:]  # The Technical Leadership section onwards
            
            # Combine
            new_full_content = part_1 + "\n" + ai_section + part_2
            
            print("   ✅ Found 'Technical Leadership' section. Injecting AI section before it...")
            
        else:
            # Fallback: If we can't find the header, append to the end
            print("   ⚠️ Could not find 'Technical Leadership' header. Appending to the end instead.")
            new_full_content = content + ai_section

        # Write the updated content back
        with open(readme_path, "w") as f:
            f.write(new_full_content)
            
        print("   ✅ README updated successfully.")

    except FileNotFoundError:
        print("   ❌ Error: README.md not found. Please check the path.")

if __name__ == "__main__":
    update_root_readme()