import pdfplumber
from concurrent.futures import ThreadPoolExecutor
from app.config import MAX_EXTRACTION_WORKERS
from app.services.audit_publisher import publish_audit_event


def extract_page_text(page_data: tuple) -> str:
    """
    Extract text from a single PDF page with error handling.

    Args:
        page_data: Tuple of (page, page_number, filename)

    Returns:
        str: Extracted text from the page, or empty string if extraction fails
    """
    page, page_num, filename = page_data
    try:
        return page.extract_text() or ""
    except Exception as e:
        # Publish audit event for failed page extraction
        publish_audit_event("PAGE_EXTRACTION_FAILED", {
            "filename": filename,
            "page_number": page_num,
            "error": str(e)
        })
        # Return empty string to continue processing other pages
        return ""


def extract_text_from_pdf(path: str, filename: str = None) -> str:
    """
    Converts a PDF into raw text for cleaning, chunking, and embedding.
    Uses parallel processing for faster extraction of large PDFs.
    Handles corrupted pages gracefully by skipping them and logging to audit.

    Args:
        path (str): Absolute path to the PDF file.
        filename (str): Original filename for audit logging.

    Returns:
        str: Extracted text (may contain newlines/extra spaces before cleaning).
    """
    # Use path as filename if not provided
    if filename is None:
        filename = path.split("/")[-1]

    with pdfplumber.open(path) as pdf:
        pages = pdf.pages
        total_pages = len(pages)

        # For small PDFs (< 10 pages), sequential is faster due to thread overhead
        if total_pages < 10:
            texts = []
            for i, page in enumerate(pages):
                text = extract_page_text((page, i + 1, filename))
                texts.append(text)
            return "".join(texts)

        # For larger PDFs, use parallel extraction
        # Prepare page data with page numbers for error reporting
        page_data = [(page, i + 1, filename) for i, page in enumerate(pages)]

        with ThreadPoolExecutor(max_workers=MAX_EXTRACTION_WORKERS) as executor:
            page_texts = list(executor.map(extract_page_text, page_data))

        # Count failed pages
        failed_pages = sum(1 for text in page_texts if text == "")
        if failed_pages > 0:
            publish_audit_event("EXTRACTION_PARTIAL_SUCCESS", {
                "filename": filename,
                "total_pages": total_pages,
                "failed_pages": failed_pages,
                "success_pages": total_pages - failed_pages
            })

        return "".join(page_texts)
