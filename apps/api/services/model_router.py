import re
from .token_counter import count_tokens

# Indicators of programming code
CODE_INDICATORS = [
    r"```[a-zA-Z]*\n",            # Markdown code blocks
    r"\bdef\s+\w+\s*\(",           # Python functions
    r"\bclass\s+\w+[\s\w]*:",      # Python/C++ classes
    r"\bimport\s+\w+",             # Python/JS imports
    r"const\s+\w+\s*=\s*",         # JavaScript variables
    r"public\s+class\s+\w+",       # Java classes
    r"<\/?[a-z][\s\S]*>",          # HTML tags
    r"select\s+.*\s+from\s+",      # SQL queries
    r"\{\s*\"[a-zA-Z0-9_-]+\"\s*\:" # JSON objects
]

SIMPLE_INDICATORS = [
    r"^(hi|hello|hey|greetings)\b",
    r"^(what is|who is|where is|when was)\b",
    r"^(translate|pronounce|define)\b",
    r"^[a-zA-Z\s\?,.!\'\"]{1,80}$" # Short generic texts
]

def analyze_prompt_complexity(prompt: str) -> dict:
    """
    Analyzes prompt text to identify code density, length, and task difficulty.
    """
    prompt_lower = prompt.lower()
    
    # 1. Check if it is code heavy
    is_code_heavy = False
    for pattern in CODE_INDICATORS:
        if re.search(pattern, prompt):
            is_code_heavy = True
            break
            
    # 2. Check if it is a simple query
    is_simple = False
    for pattern in SIMPLE_INDICATORS:
        if re.search(pattern, prompt_lower):
            is_simple = True
            break
            
    # 3. Token Length
    token_count = count_tokens(prompt)
    
    return {
        "is_code_heavy": is_code_heavy,
        "is_simple": is_simple,
        "token_count": token_count
    }

def route_prompt(prompt: str, user_preference: str = "gpt-4o") -> dict:
    """
    Intelligently routes the prompt to the most optimal, cost-efficient LLM model.
    """
    analysis = analyze_prompt_complexity(prompt)
    
    # Defaults
    recommended_model = user_preference
    reason = "Using user selected model preference."
    savings_factor = "0.0%"

    # 1. Large Context Route: Routed to Gemini Pro (Supports 1M+ context windows cleanly)
    if analysis["token_count"] > 10000:
        recommended_model = "gemini-pro"
        reason = f"Prompt payload is large ({analysis['token_count']} tokens) - routed to Google Gemini Pro for massive context support."
        savings_factor = "Up to 50% cheaper context costs"
        
    # 2. Code Refactoring Route: Routed to Claude 3.5 Sonnet (State of the art code intelligence)
    elif analysis["is_code_heavy"]:
        recommended_model = "claude-3-5-sonnet"
        reason = "Contains complex software programming syntax/code blocks - routed to Anthropic Claude 3.5 Sonnet for maximum accuracy."
        savings_factor = "Fewer iterations needed"
        
    # 3. Simple/Cheap Task Route: Routed to GPT-4o Mini (Ultra low-cost, fast)
    elif analysis["is_simple"] and analysis["token_count"] < 4000:
        recommended_model = "gpt-4o-mini"
        reason = f"Task is standard query under 4k tokens ({analysis['token_count']} tokens) - routed to OpenAI GPT-4o Mini for cost-efficiency."
        savings_factor = "97% savings compared to standard GPT-4o"
        
    return {
        "original_preference": user_preference,
        "recommended_model": recommended_model,
        "reason": reason,
        "savings_factor": savings_factor,
        "is_code_heavy": analysis["is_code_heavy"],
        "is_simple": analysis["is_simple"],
        "token_count": analysis["token_count"]
    }
