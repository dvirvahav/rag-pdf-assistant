import pdfplumber

def extract_text_from_pdf(path: str) -> str:
    """
    Extract raw text from a PDF file.

    Args:
        path (str): Full file path of the PDF.

    Returns:
        str: Raw extracted text (may contain newlines and extra spaces).
    """
    text = ""

    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            # page.extract_text() can return None -> use "" as fallback
            text += page.extract_text() or ""

    return text
