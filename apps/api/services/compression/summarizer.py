import re
import logging

logger = logging.getLogger(__name__)

# Global variables for lazy loading of the summarizer pipeline
_summarizer_pipeline = None

def get_summarizer():
    """
    Lazily initializes and returns the HuggingFace summarization pipeline.
    This saves boot memory and ensures the API starts instantly.
    """
    global _summarizer_pipeline
    if _summarizer_pipeline is None:
        try:
            logger.info("Initializing HuggingFace BART summarizer (facebook/bart-large-cnn)...")
            from transformers import pipeline
            # Using CPU by default for stability and ease of deployment on starter servers
            _summarizer_pipeline = pipeline(
                "summarization",
                model="facebook/bart-large-cnn",
                device=-1  # -1 is CPU, >=0 is GPU ID
            )
            logger.info("BART summarizer loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load HuggingFace summarizer: {e}")
            _summarizer_pipeline = "fallback"
            
    return _summarizer_pipeline

def split_context_and_instructions(text: str) -> tuple[list[dict], list[str]]:
    """
    Divides paragraphs into 'context' (eligible for summary) and 'instructions' (protected).
    A paragraph is counted as an instruction if it contains active imperative verbs or is short.
    """
    from .heuristic import contains_instruction
    
    paragraphs = text.split("\n\n")
    processed_paragraphs = []
    
    for idx, p in enumerate(paragraphs):
        p_strip = p.strip()
        if not p_strip:
            continue
            
        # Protect code blocks completely from summarization
        if "```" in p_strip:
            processed_paragraphs.append({
                "type": "code",
                "content": p_strip
            })
            continue
            
        # If paragraph contains instructions or is relatively short (< 150 chars), protect it
        if contains_instruction(p_strip) or len(p_strip) < 200:
            processed_paragraphs.append({
                "type": "instruction",
                "content": p_strip
            })
        else:
            processed_paragraphs.append({
                "type": "context",
                "content": p_strip
            })
            
    return processed_paragraphs

def compress_summarizer(text: str) -> str:
    """
    Applies Layer 3 local BART summarization.
    Compresses only long context chunks, leaving instructions and code pristine.
    """
    if not text:
        return ""
        
    segments = split_context_and_instructions(text)
    
    # We only apply summarizer if there's significant context to summarize
    has_large_context = any(seg["type"] == "context" and len(seg["content"]) > 300 for seg in segments)
    if not has_large_context:
        # If no large context is found, return the text unchanged (caller will rely on Layer 2)
        return text
        
    pipeline = get_summarizer()
    
    final_paragraphs = []
    for seg in segments:
        if seg["type"] != "context":
            final_paragraphs.append(seg["content"])
            continue
            
        context_text = seg["content"]
        
        # Only summarize long text
        if len(context_text) < 300:
            final_paragraphs.append(context_text)
            continue
            
        # Call BART pipeline
        if pipeline and pipeline != "fallback":
            try:
                # Approximate words
                word_count = len(context_text.split())
                max_len = max(30, int(word_count * 0.5))
                min_len = max(10, int(word_count * 0.25))
                
                # Truncate input if it exceeds model max length limit (~1024 tokens)
                # Keep it safe (around 800 words max per chunk for summarizer)
                chunk_words = context_text.split()
                if len(chunk_words) > 800:
                    context_chunk = " ".join(chunk_words[:800])
                else:
                    context_chunk = context_text
                    
                result = pipeline(
                    context_chunk,
                    max_length=max_len,
                    min_length=min_len,
                    do_sample=False
                )
                summary = result[0]["summary_text"]
                final_paragraphs.append(summary)
            except Exception as e:
                logger.error(f"BART summarization failed for paragraph, falling back to heuristic: {e}")
                # Fallback to a basic rule of keeping the first and last sentences
                final_paragraphs.append(fallback_summarize_paragraph(context_text))
        else:
            # Fallback to basic rule
            final_paragraphs.append(fallback_summarize_paragraph(context_text))
            
    return "\n\n".join(final_paragraphs)

def fallback_summarize_paragraph(paragraph: str) -> str:
    """
    Lightweight heuristic fallback for summarization.
    Keeps the first two and the last sentence of the context block.
    """
    from .heuristic import split_into_sentences
    sentences = split_into_sentences(paragraph)
    if len(sentences) <= 3:
        return paragraph
        
    # Keep start, middle importance indicator, and end
    return f"{sentences[0]} {sentences[1]} [...] {sentences[-1]}"
