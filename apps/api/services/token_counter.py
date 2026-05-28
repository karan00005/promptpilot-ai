import tiktoken

# Pricing per token (input pricing)
MODEL_PRICING = {
    "gpt-4o": 0.000005,         # $5.00 per 1M input tokens
    "gpt-4o-mini": 0.00000015,  # $0.15 per 1M input tokens
    "gpt-4": 0.00003,           # $30.00 per 1M input tokens
    "gpt-3.5-turbo": 0.0000005, # $0.50 per 1M input tokens
    "claude-3-5-sonnet": 0.000003, # $3.00 per 1M input tokens
    "gemini-pro": 0.0000035,    # $3.50 per 1M input tokens
}

DEFAULT_COST_PER_TOKEN = 0.000002  # $2.00 per 1M tokens fallback

def get_encoder_for_model(model_name: str):
    """
    Returns the appropriate tiktoken encoder.
    Falls back to cl100k_base if model is not recognized.
    """
    model_name_lower = model_name.lower()
    try:
        # GPT-4o uses o200k_base
        if "gpt-4o" in model_name_lower:
            return tiktoken.get_encoding("o200k_base")
        return tiktoken.encoding_for_model(model_name)
    except Exception:
        try:
            return tiktoken.get_encoding("cl100k_base")
        except Exception:
            # Fallback in case of absolute failure
            return None

def count_tokens(text: str, model: str = "gpt-4o") -> int:
    """
    Counts the number of tokens in the text using tiktoken.
    Falls back to a character/word approximation if tiktoken is not available.
    """
    if not text:
        return 0
        
    encoder = get_encoder_for_model(model)
    if encoder:
        return len(encoder.encode(text))
    
    # Simple fallback: 1 token ~= 4 chars or 0.75 words
    return max(1, int(len(text) / 4))

def estimate_cost(token_count: int, model: str = "gpt-4o") -> float:
    """
    Estimates the cost of input tokens.
    """
    model_lower = model.lower()
    cost_per_token = DEFAULT_COST_PER_TOKEN
    
    for key, rate in MODEL_PRICING.items():
        if key in model_lower:
            cost_per_token = rate
            break
            
    return round(token_count * cost_per_token, 6)
