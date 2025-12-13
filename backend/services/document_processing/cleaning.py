import re
import logging
from typing import List, Set
from backend.config import settings

logger = logging.getLogger(__name__)


def clean_text(text: str) -> str:
    """
    Advanced text cleaning with preservation of important short blocks.

    Args:
        text: Raw extracted text

    Returns:
        Cleaned text with preserved important content
    """
    if not text:
        return ""

    # Split into lines for processing
    lines = text.split('\n')

    # Clean and filter lines
    cleaned_lines = []
    for line in lines:
        cleaned_line = _clean_single_line(line)
        if cleaned_line:  # Only add non-empty lines
            cleaned_lines.append(cleaned_line)

    # Join with single newlines
    result = '\n'.join(cleaned_lines)

    # Final cleanup
    result = _final_cleanup(result)

    return result


def _clean_single_line(line: str) -> str:
    """
    Clean a single line while preserving important short content.

    Args:
        line: Single line of text

    Returns:
        Cleaned line or empty string if should be removed
    """
    if not line or not line.strip():
        return ""

    # Remove excessive whitespace
    line = re.sub(r'\s+', ' ', line.strip())

    if not line:
        return ""

    # Check if this line should be preserved
    if _should_preserve_line(line):
        return line

    # For regular lines, apply normal cleaning
    # Remove lines that are too short (but preserve important ones)
    words = line.split()
    if len(words) < settings.MIN_TEXT_BLOCK_WORDS:
        # Check for numeric values or footnote markers that should be preserved
        if not (_is_numeric_value(line) or _is_footnote_marker(line)):
            return ""  # Remove very short lines

    return line


def _should_preserve_line(line: str) -> bool:
    """
    Determine if a line should be preserved even if it's short.

    Args:
        line: Line to check

    Returns:
        True if line should be preserved
    """
    # Preserve numeric values if setting is enabled
    if settings.PRESERVE_NUMERIC_VALUES and _is_numeric_value(line):
        return True

    # Preserve footnote markers
    if _is_footnote_marker(line):
        return True

    # Preserve lines with important punctuation or formatting
    if re.search(r'[•●○■□▪▫]', line):  # Bullet points
        return True

    if re.search(r'^\s*[\d]+\.|\(\d+\)', line):  # Numbered lists
        return True

    return False


def _is_numeric_value(text: str) -> bool:
    """
    Check if text represents a numeric value that should be preserved.

    Args:
        text: Text to check

    Returns:
        True if text is a numeric value
    """
    # Remove common currency symbols and commas
    cleaned = re.sub(r'[$,€£¥₹₽₩₦₨₪₫₡₵₺₴₸₼₲₱₭₯₰₳₶₷₹₻₽₾₿]', '', text)
    cleaned = cleaned.replace(',', '').replace(' ', '')

    # Check for currency patterns
    if re.match(r'^\d+(\.\d{1,2})?$', cleaned):
        return True

    # Check for percentage
    if re.match(r'^\d+(\.\d+)?%$', cleaned):
        return True

    return False


def _is_footnote_marker(text: str) -> bool:
    """
    Check if text is a footnote marker.

    Args:
        text: Text to check

    Returns:
        True if text is a footnote marker
    """
    # Common footnote patterns: [1], (1), ¹, *, †, etc.
    patterns = [
        r'^\[\d+\]$',  # [1], [2], etc.
        r'^\(\d+\)$',  # (1), (2), etc.
        r'^[\d]+$',    # 1, 2, etc. (standalone numbers)
        r'^[*†‡§¶#]+$', # *, †, ‡, §, ¶, # symbols
        r'^[¹²³⁴⁵⁶⁷⁸⁹⁰]+$',  # Superscript numbers
    ]

    for pattern in patterns:
        if re.match(pattern, text.strip()):
            return True

    return False


def _final_cleanup(text: str) -> str:
    """
    Apply final cleanup to the entire text.

    Args:
        text: Text to clean

    Returns:
        Final cleaned text
    """
    if not text:
        return ""

    # Remove excessive newlines
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Fix spacing around punctuation
    text = re.sub(r'\s+([,.!?;:])', r'\1', text)

    # Ensure single space after punctuation
    text = re.sub(r'([,.!?;:])\s*', r'\1 ', text)

    # Remove trailing spaces from lines
    lines = [line.rstrip() for line in text.split('\n')]
    text = '\n'.join(lines)

    # Final strip
    return text.strip()


def clean_text_blocks(text_blocks: List[str]) -> List[str]:
    """
    Clean multiple text blocks while preserving document structure.

    Args:
        text_blocks: List of text blocks

    Returns:
        List of cleaned text blocks
    """
    return [clean_text(block) for block in text_blocks if clean_text(block)]


def remove_table_artifacts(text: str) -> str:
    """
    Remove common table formatting artifacts from text.

    Args:
        text: Text that may contain table artifacts

    Returns:
        Text with table artifacts removed
    """
    # Remove excessive pipes and table borders
    text = re.sub(r'[|│┌┐└┘├┤┬┴┼─]+', ' ', text)

    # Remove multiple spaces created by table removal
    text = re.sub(r'\s+', ' ', text)

    return text.strip()
