import pdfplumber


def extract_clean_text(path: str) -> str:
    """
    Full pipeline:
    1. Extract raw text from PDF
    2. Clean text (remove newlines, duplicate spaces)
    """
    text = extract_text_from_pdf(path)
    cleaned = clean_text(text)
    return cleaned

def extract_text_from_pdf(path: str) -> str:
        """
        Extracts text from a PDF file.

        Args:
            path (str): The file path of the PDF.

        Returns:
            str: Extracted text.
        """
        text = ""
        with pdfplumber.open(path) as pdf:
                for page in pdf.pages:
                        text += page.extract_text() or ""
        return text

def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> list:
       """
        Split text into overlapping chunks.
        chunk_size = size of each chunk
        overlap = number of characters reused from previous chunk
        """
       
       chunks = []
       start = 0

       while start < len(text):
              end = start + chunk_size
              chunk = text[start:end]
              chunks.append(chunk)
              start += chunk_size - overlap
       return chunks

def clean_text(text: str) -> str:
        """
        Clean text to improve RAG results.

        Args:
            text (str): raw text extracted from the PDF

        Returns:
            str: cleaned text (no newlines, no duplicate spaces)
        """
        
        # Remove repeated spaces + newlines
        text = " ".join(text.split())

        return text