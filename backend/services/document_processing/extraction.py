import pdfplumber
import os
import logging
import io
from PIL import Image
from typing import Optional
from backend.config import settings
from backend.services.document_processing.ocr import ocr_service
from backend.services.document_processing.layout import layout_analyzer, header_footer_filter
from backend.services.document_processing.types import ExtractionResult, PageResult

logger = logging.getLogger(__name__)


def extract_text_from_pdf_smart(path: str) -> ExtractionResult:
    """
    Smart PDF text extraction with OCR fallback.

    Strategy:
    1. Try text extraction first (faster, cleaner)
    2. Check text quality (<100 chars = poor quality)
    3. Fallback to OCR if text extraction fails or yields poor results
    4. Continue processing even if some pages fail

    Args:
        path (str): Full file path of the PDF.

    Returns:
        ExtractionResult: Structured result with page-by-page details.

    Raises:
        FileNotFoundError: If PDF file doesn't exist
        ValueError: If PDF is corrupted, password-protected, or empty
        RuntimeError: If extraction fails completely
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

    pages = []
    errors = []
    total_text = ""

    try:
        with pdfplumber.open(path) as pdf:
            # Check if PDF has pages
            if not pdf.pages:
                raise ValueError("PDF has no pages")

            total_pages = len(pdf.pages)

            # Process each page
            for page_num, page in enumerate(pdf.pages, start=1):
                page_result = _process_single_page(page, page_num, path)
                pages.append(page_result)

                if page_result.success and page_result.text:
                    total_text += page_result.text + "\n"
                elif not page_result.success:
                    errors.append({
                        "page_number": page_num,
                        "error": page_result.error,
                        "method": page_result.method
                    })

        # Apply header/footer filtering across all pages
        page_texts = [p.text for p in pages if p.success and p.text]
        if page_texts and settings.HEADER_FOOTER_DETECTION:
            try:
                filtered_texts = header_footer_filter.filter_headers_footers(page_texts)

                # Update pages with filtered text
                filtered_idx = 0
                for page_result in pages:
                    if page_result.success and page_result.text:
                        original_length = len(page_result.text)
                        page_result.text = filtered_texts[filtered_idx]
                        filtered_idx += 1

                        if len(page_result.text) != original_length:
                            logger.debug(f"Page {page_result.page_number}: Applied header/footer filtering")

                # Rebuild total_text with filtered content
                total_text = ""
                for page_result in pages:
                    if page_result.success and page_result.text:
                        total_text += page_result.text + "\n"

            except Exception as e:
                logger.warning(f"Header/footer filtering failed: {str(e)}")
                # Continue with unfiltered text

        # Calculate statistics
        successful_pages = sum(1 for p in pages if p.success)
        failed_pages = len(errors)

        # Determine overall success
        overall_success = successful_pages > 0  # At least one page succeeded

        if not overall_success:
            raise RuntimeError("Failed to extract text from any page in the PDF")

        result = ExtractionResult(
            success=overall_success,
            pages=pages,
            errors=errors,
            stats={
                "total_pages": total_pages,
                "successful_pages": successful_pages,
                "failed_pages": failed_pages
            },
            full_text=total_text.strip()
        )

        logger.info(f"PDF extraction complete: {successful_pages}/{total_pages} pages successful")
        return result

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


def _process_single_page(page, page_num: int, pdf_path: str) -> PageResult:
    """
    Process a single page with text extraction, layout analysis, and OCR fallback.

    Args:
        page: pdfplumber page object
        page_num: Page number (1-indexed)
        pdf_path: Path to the PDF file

    Returns:
        PageResult: Result for this page
    """
    try:
        # Try text extraction first (unless force OCR is enabled)
        if not settings.FORCE_OCR:
            page_text = page.extract_text() or ""

            # Check if text quality is poor
            if not ocr_service.is_text_quality_poor(page_text):
                # Apply layout analysis to reorder text if needed
                processed_text = _apply_layout_processing(page_text, page, page_num)

                return PageResult(
                    page_number=page_num,
                    text=processed_text,
                    method="text",
                    confidence=None,  # Text extraction doesn't provide confidence
                    success=True
                )

            logger.info(f"Page {page_num}: Text extraction yielded poor results, attempting OCR")

        # Fallback to OCR
        return _extract_with_ocr(page, page_num, pdf_path)

    except Exception as e:
        error_msg = f"Failed to process page {page_num}: {str(e)}"
        logger.error(error_msg)
        return PageResult(
            page_number=page_num,
            text="",
            method="failed",
            error=error_msg,
            success=False
        )


def _apply_layout_processing(page_text: str, page, page_num: int) -> str:
    """
    Apply layout analysis and text reordering to extracted text.

    Args:
        page_text: Raw extracted text
        page: pdfplumber page object
        page_num: Page number

    Returns:
        Processed text with layout corrections
    """
    if not page_text or not page_text.strip():
        return page_text

    try:
        # Apply column detection and text reordering
        if hasattr(page, 'chars') and page.chars:
            reordered_text = layout_analyzer.detect_columns_and_reorder(page_text, page.chars)
            if reordered_text != page_text:
                logger.debug(f"Page {page_num}: Applied column reordering")
                return reordered_text

    except Exception as e:
        logger.warning(f"Page {page_num}: Layout analysis failed: {str(e)}")
        # Continue with original text if layout analysis fails

    return page_text


def _extract_with_ocr(page, page_num: int, pdf_path: str) -> PageResult:
    """
    Extract text from a page using OCR.

    Args:
        page: pdfplumber page object
        page_num: Page number (1-indexed)
        pdf_path: Path to the PDF file

    Returns:
        PageResult: OCR result for this page
    """
    try:
        # Convert page to image using pdfplumber
        pil_image = page.to_image(resolution=300).original  # High resolution for OCR

        # Preprocess image for OCR
        processed_image = ocr_service.preprocess_image_for_ocr(pil_image)

        # Extract text with OCR
        ocr_text, confidence = ocr_service.extract_text_with_ocr(processed_image)

        # Check OCR confidence
        if confidence < settings.OCR_CONFIDENCE_THRESHOLD:
            logger.warning(f"Page {page_num}: OCR confidence {confidence:.1f}% below threshold {settings.OCR_CONFIDENCE_THRESHOLD}%")

        return PageResult(
            page_number=page_num,
            text=ocr_text,
            method="ocr",
            confidence=confidence,
            success=True
        )

    except Exception as e:
        error_msg = f"OCR failed for page {page_num}: {str(e)}"
        logger.error(error_msg)
        return PageResult(
            page_number=page_num,
            text="",
            method="ocr_failed",
            error=error_msg,
            success=False
        )


# Legacy function for backward compatibility
def extract_text_from_pdf(path: str) -> str:
    """
    Legacy function - extracts text and returns concatenated string.
    Use extract_text_from_pdf_smart() for detailed results.
    """
    result = extract_text_from_pdf_smart(path)
    return result.full_text
