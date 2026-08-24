from sentence_transformers import SentenceTransformer

_model = None


def get_model() -> SentenceTransformer:
    """Load the embedding model only when an embedding is actually needed."""
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def get_embedding(text: str) -> list[float]:
    """Generate a vector embedding locally, no API call. Same model used
    for jobs, resumes, and chat queries so all vectors are comparable."""
    if not text or not text.strip():
        return None
    embedding = get_model().encode(text[:5000], convert_to_numpy=True)
    return embedding.tolist()