import re
import logging
from typing import List, Tuple
from backend.config import settings

logger = logging.getLogger(__name__)


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> List[str]:
    """
    Smart text chunking that preserves document structure and short text blocks.

    Strategy:
    1. Split text into logical units (paragraphs, sections)
    2. Preserve short but important blocks (footnotes, captions, etc.)
    3. Create overlapping chunks while respecting boundaries
    4. Ensure minimum chunk quality

    Args:
        text: Text to chunk
        chunk_size: Target characters per chunk
        overlap: Characters to overlap between chunks

    Returns:
        List of text chunks
    """
    if not text or not text.strip():
        return []

    # First, split into logical blocks
    blocks = _split_into_logical_blocks(text)

    # Filter and preserve important short blocks
    filtered_blocks = _filter_blocks(blocks)

    # Combine blocks into chunks
    chunks = _create_chunks_from_blocks(filtered_blocks, chunk_size, overlap)

    # Final quality check
    chunks = [chunk for chunk in chunks if _is_chunk_quality(chunk)]

    logger.info(f"Created {len(chunks)} chunks from {len(filtered_blocks)} logical blocks")

    return chunks


def _split_into_logical_blocks(text: str) -> List[str]:
    """
    Split text into logical blocks (paragraphs, sections, etc.).

    Args:
        text: Full text

    Returns:
        List of logical text blocks
    """
    # Split by double newlines (paragraphs)
    blocks = re.split(r'\n\s*\n', text)

    # Further split by single newlines if blocks are too long
    refined_blocks = []
    for block in blocks:
        if len(block) > 2000:  # Very long block, might need splitting
            sub_blocks = re.split(r'\n', block)
            # Group related lines
            current_group = []
            for line in sub_blocks:
                if line.strip():
                    current_group.append(line)
                    # If group gets long enough, save it
                    if len(' '.join(current_group)) > 1000:
                        refined_blocks.append(' '.join(current_group))
                        current_group = []
                elif current_group:  # Empty line, save current group
                    refined_blocks.append(' '.join(current_group))
                    current_group = []
            if current_group:
                refined_blocks.append(' '.join(current_group))
        else:
            refined_blocks.append(block.strip())

    return [block for block in refined_blocks if block.strip()]


def _filter_blocks(blocks: List[str]) -> List[str]:
    """
    Filter blocks while preserving important short content.

    Args:
        blocks: List of text blocks

    Returns:
        Filtered list of blocks
    """
    filtered = []

    for block in blocks:
        # Always preserve blocks that meet minimum word count
        if len(block.split()) >= settings.MIN_TEXT_BLOCK_WORDS:
            filtered.append(block)
            continue

        # Check if this is a short but important block
        if _is_important_short_block(block):
            filtered.append(block)
            logger.debug(f"Preserved important short block: '{block[:50]}...'")
        else:
            logger.debug(f"Filtered short block: '{block[:50]}...'")

    return filtered


def _is_important_short_block(block: str) -> bool:
    """
    Determine if a short block should be preserved.

    Args:
        block: Text block to check

    Returns:
        True if block should be preserved
    """
    if not block or not block.strip():
        return False

    # Preserve numeric values
    if settings.PRESERVE_NUMERIC_VALUES:
        # Currency amounts, percentages, etc.
        if re.search(r'[$,€£¥₹₽₩₦₨₪₫₡₵₺₴₸₼₲₱₭₯₰₳₶₷₹₻₽₾₿]\s*\d', block):
            return True
        if re.search(r'\d+(\.\d+)?%', block):
            return True

    # Preserve footnote markers and references
    if re.match(r'^\s*[\[\(]\d+[\]\)]\s*$', block.strip()):
        return True

    # Preserve bullet points and numbered lists
    if re.match(r'^\s*[•●○■□▪▫\-\*]\s', block):
        return True
    if re.match(r'^\s*\d+[\.\)]\s', block):
        return True

    # Preserve section headers (short but important)
    if len(block.split()) <= 5 and block.isupper():  # ALL CAPS headers
        return True

    # Preserve very short but complete sentences
    words = block.split()
    if 2 <= len(words) <= 4 and block.endswith(('.', '!', '?', ':')):
        return True

    return False


def _create_chunks_from_blocks(blocks: List[str], chunk_size: int, overlap: int) -> List[str]:
    """
    Create overlapping chunks from logical blocks.

    Args:
        blocks: Logical text blocks
        chunk_size: Target chunk size
        overlap: Overlap between chunks

    Returns:
        List of text chunks
    """
    if not blocks:
        return []

    chunks = []
    current_chunk = ""
    current_size = 0

    for block in blocks:
        block_size = len(block)

        # If adding this block would exceed chunk size significantly
        if current_size + block_size > chunk_size * 1.5 and current_chunk:
            # Save current chunk
            chunks.append(current_chunk.strip())
            # Start new chunk with overlap from previous
            overlap_text = _get_overlap_text(current_chunk, overlap)
            current_chunk = overlap_text + " " + block
            current_size = len(current_chunk)
        else:
            # Add block to current chunk
            if current_chunk:
                current_chunk += " " + block
            else:
                current_chunk = block
            current_size = len(current_chunk)

    # Add final chunk
    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks


def _get_overlap_text(text: str, overlap_chars: int) -> str:
    """
    Extract overlap text from the end of a chunk.

    Args:
        text: Source text
        overlap_chars: Number of characters to overlap

    Returns:
        Overlap text
    """
    if len(text) <= overlap_chars:
        return text

    # Try to break at word boundary
    overlap_text = text[-overlap_chars:]
    last_space = overlap_text.rfind(' ')

    if last_space > overlap_chars // 2:  # Don't break too early
        return overlap_text[:last_space]

    return overlap_text


def _is_chunk_quality(chunk: str) -> bool:
    """
    Check if a chunk meets minimum quality standards.

    Args:
        chunk: Text chunk to check

    Returns:
        True if chunk is acceptable quality
    """
    if not chunk or not chunk.strip():
        return False

    # Minimum length check
    if len(chunk.strip()) < 50:  # Too short
        return False

    # Check for meaningful content (not just symbols)
    alpha_ratio = sum(1 for c in chunk if c.isalpha()) / len(chunk)
    if alpha_ratio < 0.3:  # Less than 30% alphabetic characters
        return False

    return True


def chunk_text_with_metadata(text: str, chunk_size: int = 800, overlap: int = 100) -> List[Tuple[str, dict]]:
    """
    Create chunks with metadata about their content.

    Args:
        text: Text to chunk
        chunk_size: Target chunk size
        overlap: Overlap between chunks

    Returns:
        List of (chunk_text, metadata) tuples
    """
    chunks = chunk_text(text, chunk_size, overlap)

    result = []
    for i, chunk in enumerate(chunks):
        metadata = {
            'chunk_id': i,
            'char_count': len(chunk),
            'word_count': len(chunk.split()),
            'has_numeric': bool(re.search(r'\d', chunk)),
            'has_bullets': bool(re.search(r'[•●○■□▪▫\-\*]', chunk)),
        }
        result.append((chunk, metadata))

    return result
