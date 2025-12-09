import pdfplumber
import os


def extract_text_from_pdf(path: str) -> str:
    """
    Extract raw text from a PDF file.

    Args:
        path (str): Full file path of the PDF.

    Returns:
        str: Raw extracted text (may contain newlines and extra spaces).
        
    Raises:
        FileNotFoundError: If PDF file doesn't exist
        ValueError: If PDF is corrupted, password-protected, or empty
        RuntimeError: If extraction fails
    """
    # Validate path
    if not path or not path.strip():
        raise ValueError("PDF path cannot be empty")
    
    if not os.path.exists(path):
        raise FileNotFoundError(f"PDF file not found: {path}")
    
    if not os.path.isfile(path):
        raise ValueError(f"Path is not a file: {path}")
    
    # Check file size
    file_size = os.path.getsize(path)
    if file_size == 0:
        raise ValueError("PDF file is empty (0 bytes)")
    
    try:
        text = ""
        
        with pdfplumber.open(path) as pdf:
            # Check if PDF has pages
            if not pdf.pages:
                raise ValueError("PDF has no pages")
            
            # Extract text from each page
            for page_num, page in enumerate(pdf.pages, start=1):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text
                except Exception as e:
                    # Log warning but continue with other pages
                    print(f"Warning: Failed to extract text from page {page_num}: {str(e)}")
                    continue
        
        # Check if any text was extracted
        if not text or not text.strip():
            raise ValueError("No text could be extracted from PDF. The PDF might be image-based or empty.")
        
        return text
        
    except PermissionError as e:
        raise ValueError(f"PDF is password-protected or access denied: {str(e)}")
    except Exception as e:
        # Check for common error messages
        error_msg = str(e).lower()
        if "password" in error_msg or "encrypted" in error_msg:
            raise ValueError("PDF is password-protected. Please provide an unprotected PDF.")
        elif "corrupt" in error_msg or "damaged" in error_msg:
            raise ValueError(f"PDF file appears to be corrupted: {str(e)}")
        else:
            raise RuntimeError(f"Failed to extract text from PDF: {str(e)}")
