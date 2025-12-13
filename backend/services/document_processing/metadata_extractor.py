import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import pdfplumber

logger = logging.getLogger(__name__)


def extract_document_metadata(filepath: str) -> Dict[str, Any]:
    """
    Extract comprehensive metadata from a PDF document.

    Args:
        filepath: Path to the PDF file

    Returns:
        Dictionary containing document metadata
    """
    metadata = {
        "filename": os.path.basename(filepath),
        "file_size_bytes": os.path.getsize(filepath),
        "file_size_mb": round(os.path.getsize(filepath) / (1024 * 1024), 2),
        "extraction_timestamp": datetime.now().isoformat(),
    }

    try:
        with pdfplumber.open(filepath) as pdf:
            # Basic PDF info
            metadata.update({
                "total_pages": len(pdf.pages),
                "pdf_version": getattr(pdf, 'version', None),
            })

            # PDF metadata from document properties
            pdf_metadata = pdf.metadata or {}
            metadata.update({
                "title": pdf_metadata.get('Title', ''),
                "author": pdf_metadata.get('Author', ''),
                "subject": pdf_metadata.get('Subject', ''),
                "creator": pdf_metadata.get('Creator', ''),
                "producer": pdf_metadata.get('Producer', ''),
                "creation_date": _parse_pdf_date(pdf_metadata.get('CreationDate', '')),
                "modification_date": _parse_pdf_date(pdf_metadata.get('ModDate', '')),
            })

            # Page-level information
            if pdf.pages:
                first_page = pdf.pages[0]
                metadata.update({
                    "page_width": getattr(first_page, 'width', None),
                    "page_height": getattr(first_page, 'height', None),
                    "page_orientation": _determine_orientation(first_page),
                })

            # Check for encryption/protection
            metadata.update({
                "is_encrypted": getattr(pdf, 'is_encrypted', False),
                "is_extractable": _check_text_extractable(pdf),
            })

    except Exception as e:
        logger.warning(f"Failed to extract PDF metadata: {str(e)}")
        metadata["extraction_error"] = str(e)

    return metadata


def _parse_pdf_date(date_string: str) -> Optional[str]:
    """
    Parse PDF date format (D:YYYYMMDDHHMMSS) to ISO format.

    Args:
        date_string: PDF date string

    Returns:
        ISO formatted date string or None
    """
    if not date_string or not date_string.startswith('D:'):
        return None

    try:
        # Remove 'D:' prefix and parse
        date_part = date_string[2:]

        if len(date_part) >= 14:  # YYYYMMDDHHMMSS
            year = date_part[0:4]
            month = date_part[4:6]
            day = date_part[6:8]
            hour = date_part[8:10]
            minute = date_part[10:12]
            second = date_part[12:14]

            iso_date = f"{year}-{month}-{day}T{hour}:{minute}:{second}"
            return iso_date
        elif len(date_part) >= 8:  # YYYYMMDD
            year = date_part[0:4]
            month = date_part[4:6]
            day = date_part[6:8]
            return f"{year}-{month}-{day}"

    except (ValueError, IndexError):
        pass

    return date_string  # Return original if parsing fails


def _determine_orientation(page) -> str:
    """
    Determine if page is portrait or landscape.

    Args:
        page: pdfplumber page object

    Returns:
        "portrait" or "landscape"
    """
    try:
        width = getattr(page, 'width', 0)
        height = getattr(page, 'height', 0)

        if width > height:
            return "landscape"
        else:
            return "portrait"
    except:
        return "unknown"


def _check_text_extractable(pdf) -> bool:
    """
    Check if text can be extracted from the PDF.

    Args:
        pdf: pdfplumber PDF object

    Returns:
        True if text extraction is possible
    """
    try:
        if pdf.pages:
            # Try to extract text from first page
            first_page = pdf.pages[0]
            text = first_page.extract_text() or ""
            return len(text.strip()) > 0
    except:
        pass

    return False


def format_metadata_for_context(metadata: Dict[str, Any]) -> str:
    """
    Format metadata dictionary into a readable context string.

    Args:
        metadata: Document metadata dictionary

    Returns:
        Formatted string suitable for AI context
    """
    context_parts = []

    # Basic document info
    if metadata.get('title'):
        context_parts.append(f"Title: {metadata['title']}")
    if metadata.get('author'):
        context_parts.append(f"Author: {metadata['author']}")
    if metadata.get('total_pages'):
        context_parts.append(f"Total pages: {metadata['total_pages']}")
    if metadata.get('creation_date'):
        context_parts.append(f"Created: {metadata['creation_date']}")
    if metadata.get('file_size_mb'):
        context_parts.append(f"File size: {metadata['file_size_mb']} MB")

    # Document properties
    if metadata.get('subject'):
        context_parts.append(f"Subject: {metadata['subject']}")
    if metadata.get('page_orientation') and metadata['page_orientation'] != 'unknown':
        context_parts.append(f"Page orientation: {metadata['page_orientation']}")

    if context_parts:
        return "Document Information: " + "; ".join(context_parts)
    else:
        return "Document Information: Basic PDF document"


def get_metadata_summary(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get a summary of key metadata for API responses.

    Args:
        metadata: Full metadata dictionary

    Returns:
        Summary dictionary with key fields
    """
    return {
        "filename": metadata.get("filename", ""),
        "total_pages": metadata.get("total_pages", 0),
        "file_size_mb": metadata.get("file_size_mb", 0),
        "author": metadata.get("author", ""),
        "title": metadata.get("title", ""),
        "creation_date": metadata.get("creation_date", ""),
        "is_encrypted": metadata.get("is_encrypted", False),
    }
