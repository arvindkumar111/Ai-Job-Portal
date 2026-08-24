import hashlib
import re

def normalize_text(text: str | None) -> str:
    """Lowercase, strip whitespace/punctuation noise so near-identical
    strings hash the same way."""
    if not text:
        return ""
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)        # collapse multiple spaces
    text = re.sub(r"[^\w\s]", "", text)     # strip punctuation
    return text

def compute_content_hash(title: str, company: str, location: str) -> str:
    """Exact-duplicate fingerprint: same normalized title+company+location
    = same job, regardless of platform or minor formatting differences."""
    key = f"{normalize_text(title)}|{normalize_text(company)}|{normalize_text(location)}"
    return hashlib.sha256(key.encode()).hexdigest()