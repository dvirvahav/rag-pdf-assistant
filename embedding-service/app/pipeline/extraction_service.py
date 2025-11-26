import pdfplumber

def extract_text_from_pdf(path: str) -> str:
    """
    Converts a PDF into raw text for cleaning, chunking, and embedding.

    Args:
        path (str): Absolute path to the PDF file.

    Returns:
        str: Extracted text (may contain newlines/extra spaces before cleaning).
    """
    text = ""

    # Open and read PDF safely
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            # page.extract_text() may return None -> fallback to empty string
            page_text = page.extract_text() or ""
            text += page_text

    return text
