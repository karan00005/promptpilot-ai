import logging

logger = logging.getLogger(__name__)

# Global variables for lazy loading LLMLingua
_llmlingua_compressor = None

def get_llmlingua_compressor():
    """
    Lazily loads and initializes Microsoft LLMLingua-2 compressor.
    Saves memory and starts the API server instantly.
    """
    global _llmlingua_compressor
    if _llmlingua_compressor is None:
        try:
            logger.info("Initializing Microsoft LLMLingua-2 compressor model...")
            from llmlingua import PromptCompressor
            
            # Using the fast, lightweight LLMLingua-2 BERT model
            _llmlingua_compressor = PromptCompressor(
                model_name="microsoft/llmlingua-2-bert-base-multilingual-cased-meetingbank",
                use_llmlingua2=True,
                device_map="cpu" # CPU-only fallback for standard servers
            )
            logger.info("LLMLingua-2 model loaded successfully!")
        except Exception as e:
            logger.error(f"Failed to load LLMLingua model: {e}. Falling back to standard pipeline.")
            _llmlingua_compressor = "fallback"
            
    return _llmlingua_compressor

def compress_llmlingua(text: str, target_rate: float = None) -> str:
    """
    Compresses prompt using LLMLingua-2 algorithm.
    Forces retention of punctuation marks to preserve semantic intent.
    Falls back to normal pipeline if model is unavailable.
    
    If target_rate is None (or default), it dynamically adjusts the target rate 
    based on the length of the input text to maximize token savings on longer prompts:
    - Very short prompts (< 500 chars): Keep 85% (prune 15%)
    - Short/medium prompts (500 - 1500 chars): Keep 65% (prune 35%)
    - Medium/long prompts (1500 - 4000 chars): Keep 50% (prune 50%)
    - Extremely long contexts (> 4000 chars): Keep 35% (prune 65% to save tokens)
    """
    if not text:
        return ""
        
    # 1. Compute dynamic target rate to maximize savings while protecting shorter prompts
    char_len = len(text)
    if target_rate is None or target_rate == 0.6:  # Default fallback overrides
        if char_len <= 500:
            dynamic_rate = 0.85
        elif char_len <= 1500:
            dynamic_rate = 0.65
        elif char_len <= 4000:
            dynamic_rate = 0.50
        else:
            dynamic_rate = 0.35
        
        logger.info(f"[Dynamic LLMLingua] Computed dynamic compression rate: {dynamic_rate} (length: {char_len} chars)")
        target_rate = dynamic_rate
        
    compressor = get_llmlingua_compressor()
    
    if compressor and compressor != "fallback":
        try:
            # Run LLMLingua compression
            result = compressor.compress_prompt(
                text,
                rate=target_rate,
                force_tokens=['\n', '?', '.', '!', ':', '-', '*'],
                drop_consecutive=True
            )
            compressed_prompt = result.get("compressed_prompt", text)
            logger.info(f"[LLMLingua] Compressed prompt successfully. Dynamic Rate: {target_rate}")
            return compressed_prompt
        except Exception as e:
            logger.error(f"LLMLingua prompt compression failed, using heuristic: {e}")
            return text
            
    return text
