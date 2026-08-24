from sentence_transformers import SentenceTransformer

# Loaded once at module import time — reused across all embedding calls.
# all-MiniLM-L6-v2 outputs 384-dimensional vectors, is fast on CPU,
# and is a standard, well-understood choice for semantic similarity tasks.
_model = SentenceTransformer("all-MiniLM-L6-v2")

def get_embedding(text: str) -> list[float]:
    """Generate a vector embedding locally, no API call. Same model used
    for jobs, resumes, and chat queries so all vectors are comparable."""
    if not text or not text.strip():
        return None
    embedding = _model.encode(text[:5000], convert_to_numpy=True)
    return embedding.tolist()