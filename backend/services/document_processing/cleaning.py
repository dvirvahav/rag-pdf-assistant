import re

def clean_text(text: str) -> str:
    """
    Clean extracted PDF text to improve chunking and embedding quality.
    Removes extra spaces, newlines, and non-readable characters.
    """

    # Replace multiple spaces/newlines with a single space
    cleaned = re.sub(r"\s+", " ", text)

    # Strip leading/trailing spaces
    cleaned = cleaned.strip()

    return cleaned
