import re

# Redundant phrases and their concise equivalents
VERBOSE_PHRASES = {
    r"\bin order to\b": "to",
    r"\bdue to the fact that\b": "because",
    r"\bas a matter of fact\b": "in fact",
    r"\bat the present time\b": "currently",
    r"\bfor the purpose of\b": "to",
    r"\bwith reference to\b": "about",
    r"\bin the event that\b": "if",
    r"\ba large number of\b": "many",
    r"\bmake a decision\b": "decide",
    r"\btake into consideration\b": "consider",
    r"\bconduct an investigation\b": "investigate",
    r"\bprovide assistance to\b": "assist",
    r"\bat this point in time\b": "now",
    r"\bso as to\b": "to",
    r"\bwith the exception of\b": "except",
    r"\bhas the ability to\b": "can",
    r"\bplays an important role in\b": "affects",
    r"\bin a timely manner\b": "quickly",
    r"\bby means of\b": "by",
    r"\bfor the reason that\b": "because",
}

# Polite filler words/clauses to strip entirely (along with surrounding punctuation/whitespace if needed)
FILLER_PATTERNS = [
    r"\bplease\b",
    r"\bkindly\b",
    r"\bcould you\b",
    r"\bi was wondering if you could\b",
    r"\bi would appreciate it if you could\b",
    r"\bwould you mind\b",
    r"\bif you don't mind\b",
    r"\bit would be great if you could\b",
    r"\bcan you please\b",
    r"\bi am writing to ask you to\b",
    r"\bhope you are doing well\b",
    r"\bhello\b",
    r"\bhi\b",
    r"\bthanks in advance\b",
    r"\bthank you in advance\b",
    r"\bthank you\b",
    r"\bthanks\b",
]

def compress_rule_based(text: str) -> str:
    """
    Applies rule-based prompt cleaning.
    Removes politeness, duplicate spacings, and optimizes verbose constructs.
    """
    if not text:
        return ""
        
    compressed = text
    
    # 1. Replace verbose phrases (case-insensitive)
    for verbose, concise in VERBOSE_PHRASES.items():
        compressed = re.sub(verbose, concise, compressed, flags=re.IGNORECASE)
        
    # 2. Strip filler patterns (case-insensitive)
    for pattern in FILLER_PATTERNS:
        # Match pattern and try to clean up double spaces/commas caused by removal
        compressed = re.sub(pattern + r",?\s*", "", compressed, flags=re.IGNORECASE)
        
    # 3. Clean up formatting (double spaces, trailing/leading spaces, excess blank lines)
    # Replace 3 or more newlines with double newlines
    compressed = re.sub(r"\n{3,}", "\n\n", compressed)
    # Replace multiple spaces with a single space (but preserve indentation if it's code/markdown)
    compressed = re.sub(r"[ \t]+", " ", compressed)
    
    # Trim leading/trailing spaces on each line
    lines = [line.strip() for line in compressed.split("\n")]
    compressed = "\n".join(lines).strip()
    
    return compressed
