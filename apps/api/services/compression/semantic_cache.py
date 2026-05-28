import logging
import json
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

logger = logging.getLogger(__name__)

def chunk_text(text: str, chunk_size_words: int = 80, overlap_words: int = 15) -> list[str]:
    """
    Semantic paragraph chunking.
    Splits text by sliding window of words to preserve semantic paragraph boundaries.
    """
    if not text:
        return []
        
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk_words = words[i : i + chunk_size_words]
        chunk_text = " ".join(chunk_words).strip()
        if chunk_text:
            chunks.append(chunk_text)
        if i + chunk_size_words >= len(words):
            break
        i += (chunk_size_words - overlap_words)
        
    return chunks

def index_document_in_db(user_id: str, title: str, original_text: str) -> dict:
    """
    Splits the original text into semantic chunks and saves them in SQLite.
    Overwrites previous contexts with the same title dynamically.
    """
    from services.local_db import save_context_document, save_context_chunks
    
    # 1. Chunk document
    chunks = chunk_text(original_text, chunk_size_words=80, overlap_words=15)
    if not chunks:
        raise ValueError("Document contains no readable text.")
        
    # 2. Save document record
    doc_id = save_context_document(user_id, title, original_text)
    
    # 3. Store chunks. Since we fit TF-IDF dynamically at search time, vector_json can be blank
    chunks_data = [(chunk, "{}") for chunk in chunks]
    success = save_context_chunks(doc_id, chunks_data)
    
    return {
        "doc_id": doc_id,
        "title": title,
        "chunks_count": len(chunks),
        "success": success
    }

def retrieve_relevant_chunks(user_id: str, title: str, query: str, top_k: int = 3) -> list[str]:
    """
    High-performance semantic retrieval engine.
    Fetches chunks for the document title, fits an L2-normalized TF-IDF vectorizer,
    and computes cosine similarity (dot products) to extract the Top-K matching segments.
    """
    from services.local_db import get_context_chunks_by_title
    
    # 1. Fetch chunks from SQLite
    chunks_records = get_context_chunks_by_title(user_id, title)
    if not chunks_records:
        logger.warning(f"No chunks found for user context doc title: '{title}'")
        return []
        
    chunks = [r["chunk_text"] for r in chunks_records]
    
    # 2. Add query to the corpus to fit TF-IDF
    corpus = chunks + [query]
    
    try:
        # L2 normalization is enabled by default in TfidfVectorizer
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(corpus)
        
        # tfidf_matrix is of shape (len(corpus), vocab_size)
        # Query vector is the last row, chunk vectors are the preceding rows
        tfidf_dense = tfidf_matrix.toarray()
        chunk_vectors = tfidf_dense[:-1]
        query_vector = tfidf_dense[-1]
        
        # Since TfidfVectorizer vectors are L2-normalized (magnitude = 1.0),
        # Cosine Similarity is EXACTLY equal to the Dot Product!
        similarities = np.dot(chunk_vectors, query_vector)
        
        # Sort indices in descending order of similarity
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        # Retrieve matching chunks
        matched_chunks = []
        for idx in top_indices:
            score = float(similarities[idx])
            # Only include chunks that have a positive semantic overlap score
            if score > 0.0:
                matched_chunks.append(chunks[idx])
                
        logger.info(f"[Semantic Cache] Searched {len(chunks)} chunks of '{title}'. Found {len(matched_chunks)} matches.")
        return matched_chunks
    except Exception as e:
        logger.error(f"Semantic search vectorization calculation failed: {e}. Falling back to default top chunks.")
        # Graceful fallback: return first top_k chunks
        return chunks[:top_k]
