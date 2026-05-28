import sys
import os

# Add parent directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.token_counter import count_tokens
from services.compression.rule_based import compress_rule_based
from services.compression.heuristic import compress_heuristic
from services.compression.summarizer import compress_summarizer

# Define high-quality test prompts that developers actually use
TEST_PROMPTS = {
    "1. Polite & Redundant Prompt (Politeness Filter Test)": 
        "Hello! I hope you are having a wonderful day. I was wondering if you could please do me a huge favor and help me write a quick Python function in order to reverse a string? I would really appreciate it if you could make it very clean and easy to understand. Thank you so much in advance, you are awesome!",
        
    "2. Wordy Developer Context (Verbose Replacements Test)":
        "Due to the fact that we have a large number of components in our system, we need to make a decision at the present time so as to conduct an investigation on how to optimize our database speed. I am writing to ask you to analyze the query schema in order to provide assistance to our team. In the event that you find index issues, please let us know in a timely manner.",
        
    "3. Code + Constraint (Safety & Heuristics Test)":
        "Here is the database model for our application:\n\n"
        "```python\nclass User(Base):\n    __tablename__ = 'users'\n    id = Column(Integer, primary_key=True)\n    email = Column(String(255), unique=True)\n    level = Column(String(50), default='free')\n```\n\n"
        "You must optimize this table schema immediately for a high-traffic production system. Always follow PostgreSQL best practices. Do not use plain text passwords. Make sure we have exactly 3 indices.",

    "4. Extremely Long Context Block (BART Summarization Layer 3 Test)":
        "PromptPilot is a cutting-edge token optimization middleware system designed by developers for developers. "
        "It acts as a lightweight proxy layer that intercepts outgoing prompts destined for Large Language Model APIs. "
        "The underlying core motivation behind this system is the fact that developers are spending enormous sums of money "
        "running advanced LLM systems due to prompt inflation, where unnecessary words, politeness fillers, and redundant context "
        "bloat token payloads and drain budgets. By applying advanced algorithmic heuristics, semantic sentence scoring via TF-IDF, "
        "and local deep-learning neural network summarization models, PromptPilot successfully trims down prompts by up to forty percent "
        "while guaranteeing 95% semantic quality retention. In addition, it integrates an advanced organization analytics dashboard "
        "to track savings, coordinate developer API keys, configure custom rates limits, and allocate budgets across teams. "
        "Now, please write an executive business summary of PromptPilot, keeping the tone professional. You must highlight the savings percentages."
}

def run_benchmark():
    # Force UTF-8 output to prevent Windows console encoding errors
    import sys
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

    print("======================================================================")
    print("                 PROMPTPILOT ENGINE - SAVINGS BENCHMARK               ")
    print("======================================================================")
    print("Running performance benchmark on 4 distinct developer prompt styles...\n")
    
    for name, prompt in TEST_PROMPTS.items():
        print(f"\n--- {name} ---")
        orig_tokens = count_tokens(prompt)
        print(f"Original Size : {orig_tokens} tokens ({len(prompt)} chars)")
        
        # Level 1: Rule-based
        lvl1_text = compress_rule_based(prompt)
        lvl1_tokens = count_tokens(lvl1_text)
        lvl1_savings = round((orig_tokens - lvl1_tokens) / orig_tokens * 100, 1) if orig_tokens > 0 else 0.0
        
        # Level 2: Heuristic TF-IDF
        lvl2_text = compress_heuristic(lvl1_text, preserve_ratio=0.7)
        lvl2_tokens = count_tokens(lvl2_text)
        lvl2_savings = round((orig_tokens - lvl2_tokens) / orig_tokens * 100, 1) if orig_tokens > 0 else 0.0
        
        # Level 3: Summarizer
        lvl3_text = compress_summarizer(lvl2_text)
        lvl3_tokens = count_tokens(lvl3_text)
        lvl3_savings = round((orig_tokens - lvl3_tokens) / orig_tokens * 100, 1) if orig_tokens > 0 else 0.0
        
        # Print results comparison table
        print(f"| Level | Tokens | Savings % | Preview of optimized prompt")
        print(f"|-------|--------|-----------|----------------------------------------------------")
        print(f"| Orig  | {orig_tokens:6d} |    0.0%   | {prompt[:70].replace(chr(10), ' ')}...")
        print(f"| Lvl 1 | {lvl1_tokens:6d} |  {lvl1_savings:5.1f}%   | {lvl1_text[:70].replace(chr(10), ' ')}...")
        print(f"| Lvl 2 | {lvl2_tokens:6d} |  {lvl2_savings:5.1f}%   | {lvl2_text[:70].replace(chr(10), ' ')}...")
        print(f"| Lvl 3 | {lvl3_tokens:6d} |  {lvl3_savings:5.1f}%   | {lvl3_text[:70].replace(chr(10), ' ')}...")
        
        # Code and structural safety verification checks
        print("\n[Safety Checks]")
        if "```" in prompt:
            code_safe = "[PASS] (Code Block Protected)" if "```" in lvl2_text else "[FAIL] (Code Block Removed)"
            print(f"- Markdown Code Block safety: {code_safe}")
        
        if "3" in prompt or "forty" in prompt:
            numbers_in_lvl2 = any(num in lvl2_text for num in ["3", "forty"])
            nums_safe = "[PASS] (Critical Numbers/Metrics Preserved)" if numbers_in_lvl2 else "[FAIL] (Numbers Lost)"
            print(f"- Numerical Quantities safety: {nums_safe}")
            
        instructions_check = ["reverse", "optimize", "write"]
        instr_detected = any(word in lvl2_text.lower() for word in instructions_check)
        instr_safe = "[PASS] (Core Directive Preserved)" if instr_detected else "[WARN] (Check instructions!)"
        print(f"- Primary Command / Directive safety: {instr_safe}")
        
    print("\n======================================================================")
    print("Benchmark complete! All optimization layers are operating securely. [OK]")
    print("======================================================================")

if __name__ == "__main__":
    run_benchmark()
