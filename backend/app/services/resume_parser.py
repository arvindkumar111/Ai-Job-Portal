from pypdf import PdfReader
from docx import Document
import io

def extract_text_from_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    text_parts = []
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text_parts.append(extracted)
    return "\n".join(text_parts)

def extract_text_from_docx(file_bytes: bytes) -> str:
    doc = Document(io.BytesIO(file_bytes))
    return "\n".join(para.text for para in doc.paragraphs if para.text.strip())

def extract_resume_text(filename: str, file_bytes: bytes) -> str | None:
    """Dispatches to the right extractor based on file extension.
    Returns None (not an exception) for unsupported types or extraction
    failures — the caller decides how to handle that gracefully."""
    lower_name = filename.lower()

    try:
        if lower_name.endswith(".pdf"):
            return extract_text_from_pdf(file_bytes)
        elif lower_name.endswith(".docx"):
            return extract_text_from_docx(file_bytes)
        else:
            return None
    except Exception as e:
        print(f"Resume extraction failed for '{filename}': {e}")
        return None