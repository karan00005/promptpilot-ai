import re
from sklearn.feature_extraction.text import TfidfVectorizer

# Directives that indicate a critical instruction sentence
INSTRUCTION_KEYWORDS = {
    "generate", "write", "create", "analyze", "explain", "how", "why", "code",
    "must", "should", "don't", "never", "always", "implement", "optimize",
    "describe", "compare", "list", "summarize", "evaluate", "predict"
}

def split_into_sentences(text: str) -> list[str]:
    """
    Splits text into sentences using regex, avoiding splitting on standard abbreviations.
    """
    if not text:
        return []
    # Avoid splitting on abbreviations like e.g., i.e., Mr., Dr., etc.
    sentence_end = re.compile(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|!)\s')
    sentences = sentence_end.split(text)
    return [s.strip() for s in sentences if s.strip()]

def is_code_block(text: str) -> bool:
    """
    Checks if a block contains markdown triple backticks.
    """
    return "```" in text

def contains_instruction(sentence: str) -> bool:
    """
    Checks if the sentence contains instruction/directive keywords.
    """
    sentence_lower = sentence.lower()
    words = set(re.findall(r'\b\w+\b', sentence_lower))
    return not words.isdisjoint(INSTRUCTION_KEYWORDS)

def contains_numbers(sentence: str) -> bool:
    """
    Checks if a sentence contains numerical values, which are usually important data points.
    """
    return bool(re.search(r'\b\d+(?:\.\d+)?\b', sentence))

def compress_heuristic(text: str, preserve_ratio: float = 0.75) -> str:
    """
    Applies Layer 2 Heuristic TF-IDF sentence trimming.
    Identifies low-importance context sentences and removes them,
    while safeguarding critical instructions, code blocks, and data points.
    """
    if not text:
        return ""
        
    # Extract code blocks first to protect them entirely from tokenization/sentence splitting
    code_blocks = []
    # Regex to find all ```blocks```
    def code_replacer(match):
        code_blocks.append(match.group(0))
        return f"\n__CODE_BLOCK_PLACEHOLDER_{len(code_blocks)-1}__\n"
        
    processed_text = re.sub(r'```.*?```', code_replacer, text, flags=re.DOTALL)
    
    # Split the rest of the text into lines/paragraphs first to preserve layout
    paragraphs = processed_text.split("\n\n")
    compressed_paragraphs = []
    
    for paragraph in paragraphs:
        if not paragraph.strip():
            continue
            
        # If it contains a code placeholder, preserve it verbatim
        if "__CODE_BLOCK_PLACEHOLDER_" in paragraph:
            compressed_paragraphs.append(paragraph)
            continue
            
        # Otherwise, process the sentences in the paragraph
        sentences = split_into_sentences(paragraph)
        if len(sentences) <= 2:
            # Short paragraph, keep it entirely
            compressed_paragraphs.append(paragraph)
            continue
            
        # Score sentences using TF-IDF
        try:
            # We treat sentences in this paragraph as documents to score term importance
            vectorizer = TfidfVectorizer(stop_words='english')
            tfidf_matrix = vectorizer.fit_transform(sentences)
            # Sum up TF-IDF scores for each sentence
            scores = tfidf_matrix.sum(axis=1).A1
        except Exception:
            # Fallback if TF-IDF fails (e.g. no vocab or single term)
            scores = [1.0] * len(sentences)
            
        # Determine sentence categories
        scored_sentences = []
        for idx, (sentence, score) in enumerate(zip(sentences, scores)):
            # Force preserve instructions and numbers
            is_critical = contains_instruction(sentence) or contains_numbers(sentence)
            scored_sentences.append({
                'text': sentence,
                'score': score,
                'is_critical': is_critical,
                'original_idx': idx
            })
            
        # Sort non-critical sentences by score to find the lowest
        non_critical = [s for s in scored_sentences if not s['is_critical']]
        non_critical.sort(key=lambda x: x['score'])
        
        # Calculate how many to keep
        target_count = max(1, int(len(sentences) * preserve_ratio))
        critical_count = len(scored_sentences) - len(non_critical)
        
        # We need to select which non-critical sentences to keep
        non_critical_to_keep_count = max(0, target_count - critical_count)
        
        # Mark the top scoring non-critical sentences to keep
        kept_non_critical_indices = set()
        if non_critical_to_keep_count > 0:
            # The highest-scoring non-critical sentences are at the end after sorting
            kept_non_critical = non_critical[-non_critical_to_keep_count:]
            kept_non_critical_indices = {s['original_idx'] for s in kept_non_critical}
            
        # Assemble back in original order
        final_sentences = []
        for s in scored_sentences:
            if s['is_critical'] or s['original_idx'] in kept_non_critical_indices:
                final_sentences.append(s['text'])
                
        if final_sentences:
            compressed_paragraphs.append(" ".join(final_sentences))
            
    # Reassemble paragraphs
    compressed_text = "\n\n".join(compressed_paragraphs)
    
    # Restore code blocks
    for idx, code_content in enumerate(code_blocks):
        compressed_text = compressed_text.replace(
            f"__CODE_BLOCK_PLACEHOLDER_{idx}__",
            code_content
        )
        
    return compressed_text.strip()
