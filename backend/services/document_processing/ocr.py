import pytesseract
from PIL import Image
import io
import logging
from typing import Optional, Tuple
from backend.config import settings

logger = logging.getLogger(__name__)


class OCRService:
    """
    OCR service for processing scanned PDFs and images.
    Uses Tesseract OCR with confidence scoring.
    """

    def __init__(self):
        # Configure Tesseract if needed
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Windows
        pass

    def extract_text_with_ocr(self, image: Image.Image) -> Tuple[str, float]:
        """
        Extract text from image using OCR.

        Args:
            image: PIL Image object

        Returns:
            Tuple of (extracted_text, confidence_score)
        """
        try:
            # Get detailed OCR data including confidence scores
            ocr_data = pytesseract.image_to_data(
                image,
                output_type=pytesseract.Output.DICT,
                config='--psm 6'  # Uniform block of text
            )

            # Extract text and calculate average confidence
            text_parts = []
            confidences = []

            for i, confidence in enumerate(ocr_data['conf']):
                if int(confidence) > 0:  # Filter out negative confidences
                    text = ocr_data['text'][i].strip()
                    if text:
                        text_parts.append(text)
                        confidences.append(int(confidence))

            extracted_text = ' '.join(text_parts)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

            logger.info(f"OCR extracted {len(extracted_text)} characters with {avg_confidence:.1f}% confidence")

            return extracted_text, avg_confidence

        except Exception as e:
            logger.error(f"OCR extraction failed: {str(e)}")
            return "", 0.0

    def get_confidence_score(self, ocr_data: dict) -> float:
        """
        Calculate average confidence score from OCR data.

        Args:
            ocr_data: OCR data dictionary from pytesseract

        Returns:
            Average confidence score (0-100)
        """
        confidences = [int(conf) for conf in ocr_data['conf'] if int(conf) > 0]
        return sum(confidences) / len(confidences) if confidences else 0.0

    def is_text_quality_poor(self, text: str) -> bool:
        """
        Determine if extracted text is of poor quality and needs OCR fallback.

        Args:
            text: Extracted text to evaluate

        Returns:
            True if text quality is poor and OCR should be attempted
        """
        if not text or not text.strip():
            return True

        # Check minimum length
        if len(text.strip()) < settings.MIN_TEXT_LENGTH_FOR_OCR_FALLBACK:
            return True

        # Check for garbled content (high ratio of non-alphanumeric characters)
        alphanumeric = sum(1 for c in text if c.isalnum() or c.isspace())
        if alphanumeric / len(text) < 0.5:  # Less than 50% alphanumeric
            return True

        return False

    def preprocess_image_for_ocr(self, image: Image.Image) -> Image.Image:
        """
        Preprocess image to improve OCR accuracy.

        Args:
            image: PIL Image to preprocess

        Returns:
            Preprocessed PIL Image
        """
        # Convert to grayscale if not already
        if image.mode != 'L':
            image = image.convert('L')

        # Enhance contrast (simple approach)
        # Could add more sophisticated preprocessing here

        return image


# Global OCR service instance
ocr_service = OCRService()
