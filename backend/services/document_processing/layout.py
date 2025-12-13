import re
import logging
from typing import List, Dict, Any, Tuple, Optional
from backend.config import settings

logger = logging.getLogger(__name__)


class LayoutAnalyzer:
    """
    Analyzes PDF page layout for multi-column detection and text reordering.
    """

    def __init__(self):
        pass

    def detect_columns_and_reorder(self, page_text: str, page_chars: List[Dict]) -> str:
        """
        Detect multi-column layout and reorder text for proper reading order.

        Args:
            page_text: Raw extracted text from pdfplumber
            page_chars: Character-level data from pdfplumber page.chars

        Returns:
            Reordered text in proper reading order
        """
        if not settings.COLUMN_DETECTION_ENABLED or not page_chars:
            return page_text

        # Detect column layout
        columns = self._detect_columns(page_chars)

        if len(columns) <= 1:
            # Single column or no clear columns detected
            return page_text

        # Limit to max columns setting
        columns = columns[:settings.MAX_COLUMNS]

        logger.info(f"Detected {len(columns)} columns, reordering text")

        # Extract text from each column and reorder
        reordered_texts = []
        for col_bbox in columns:
            column_text = self._extract_text_from_bbox(page_text, page_chars, col_bbox)
            if column_text.strip():
                reordered_texts.append(column_text)

        # Join columns with proper spacing
        return '\n\n'.join(reordered_texts)

    def _detect_columns(self, page_chars: List[Dict]) -> List[Tuple[float, float, float, float]]:
        """
        Detect column boundaries using character position clustering.

        Args:
            page_chars: Character data from pdfplumber

        Returns:
            List of column bounding boxes (x0, y0, x1, y1)
        """
        if not page_chars:
            return []

        # Extract x-coordinates of all characters
        x_positions = [char['x0'] for char in page_chars if 'x0' in char]

        if len(x_positions) < 10:  # Not enough data for reliable detection
            return []

        # Find clusters in x-positions (potential column starts)
        clusters = self._find_x_clusters(x_positions)

        if len(clusters) <= 1:
            return []

        # Convert clusters to column bounding boxes
        columns = []
        page_width = max((char.get('x1', 0) for char in page_chars), default=0)
        page_height = max((char.get('y1', 0) for char in page_chars), default=0)

        for i, cluster_x in enumerate(sorted(clusters.keys())):
            # Define column width based on cluster spacing
            if i < len(clusters) - 1:
                next_cluster = sorted(clusters.keys())[i + 1]
                col_width = next_cluster - cluster_x
            else:
                col_width = page_width - cluster_x

            # Create bounding box for this column
            col_bbox = (cluster_x, 0, cluster_x + col_width, page_height)
            columns.append(col_bbox)

        return columns

    def _find_x_clusters(self, x_positions: List[float], threshold: float = 50) -> Dict[float, int]:
        """
        Find clusters of x-positions that indicate column starts.

        Args:
            x_positions: List of x-coordinates
            threshold: Maximum distance to be considered same cluster

        Returns:
            Dict of cluster centers and their sizes
        """
        if not x_positions:
            return {}

        # Sort positions
        sorted_x = sorted(x_positions)

        clusters = {}
        current_cluster = [sorted_x[0]]
        current_center = sorted_x[0]

        for x in sorted_x[1:]:
            if x - current_center <= threshold:
                current_cluster.append(x)
                current_center = sum(current_cluster) / len(current_cluster)
            else:
                # Save current cluster
                clusters[current_center] = len(current_cluster)
                # Start new cluster
                current_cluster = [x]
                current_center = x

        # Save last cluster
        if current_cluster:
            clusters[current_center] = len(current_cluster)

        # Filter clusters that are too small (likely noise)
        min_cluster_size = max(5, len(x_positions) // 20)  # At least 5% of characters
        return {k: v for k, v in clusters.items() if v >= min_cluster_size}

    def _extract_text_from_bbox(self, page_text: str, page_chars: List[Dict],
                               bbox: Tuple[float, float, float, float]) -> str:
        """
        Extract text that falls within a bounding box.

        Args:
            page_text: Full page text (fallback)
            page_chars: Character data
            bbox: Bounding box (x0, y0, x1, y1)

        Returns:
            Text within the bounding box
        """
        x0, y0, x1, y1 = bbox

        # Filter characters within bbox
        column_chars = [
            char for char in page_chars
            if x0 <= char.get('x0', 0) <= x1 and y0 <= char.get('y0', 0) <= y1
        ]

        if not column_chars:
            return ""

        # Sort by y (top to bottom), then by x (left to right)
        column_chars.sort(key=lambda c: (c.get('y0', 0), c.get('x0', 0)))

        # Reconstruct text from characters
        text_parts = []
        current_line = []
        current_y = None
        line_threshold = 5  # pixels

        for char in column_chars:
            char_text = char.get('text', '')
            char_y = char.get('y0', 0)

            if current_y is None:
                current_y = char_y
                current_line.append(char_text)
            elif abs(char_y - current_y) <= line_threshold:
                # Same line
                current_line.append(char_text)
            else:
                # New line
                if current_line:
                    text_parts.append(''.join(current_line))
                current_line = [char_text]
                current_y = char_y

        # Add last line
        if current_line:
            text_parts.append(''.join(current_line))

        return '\n'.join(text_parts)


class HeaderFooterFilter:
    """
    Detects and filters headers and footers from extracted text.
    """

    def __init__(self):
        self.header_patterns = []
        self.footer_patterns = []

    def filter_headers_footers(self, pages: List[str]) -> List[str]:
        """
        Remove headers and footers from multiple pages.

        Args:
            pages: List of page texts

        Returns:
            List of cleaned page texts
        """
        if not settings.HEADER_FOOTER_DETECTION or len(pages) < 2:
            return pages

        # Detect repeating patterns
        self._detect_repeating_patterns(pages)

        # Apply filtering to each page
        filtered_pages = []
        for i, page_text in enumerate(pages):
            filtered_text = self._filter_single_page(page_text, i + 1, len(pages))
            filtered_pages.append(filtered_text)

        return filtered_pages

    def _detect_repeating_patterns(self, pages: List[str]):
        """Detect headers/footers by finding repeated content across pages."""
        if len(pages) < 3:
            return

        # Get first few lines of each page
        first_lines = []
        last_lines = []

        for page in pages:
            lines = page.split('\n')[:3]  # First 3 lines
            first_lines.append(' '.join(lines).strip())

            lines = page.split('\n')[-3:]  # Last 3 lines
            last_lines.append(' '.join(lines).strip())

        # Find patterns that repeat across multiple pages
        self.header_patterns = self._find_repeating_patterns(first_lines)
        self.footer_patterns = self._find_repeating_patterns(last_lines)

        logger.info(f"Detected {len(self.header_patterns)} header patterns, {len(self.footer_patterns)} footer patterns")

    def _find_repeating_patterns(self, text_samples: List[str], min_occurrences: int = 3) -> List[str]:
        """Find text patterns that appear in multiple samples."""
        pattern_counts = {}

        for sample in text_samples:
            # Look for common patterns (page numbers, titles, etc.)
            patterns = self._extract_potential_patterns(sample)
            for pattern in patterns:
                pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1

        # Return patterns that appear in at least min_occurrences samples
        return [pattern for pattern, count in pattern_counts.items() if count >= min_occurrences]

    def _extract_potential_patterns(self, text: str) -> List[str]:
        """Extract potential header/footer patterns from text."""
        patterns = []

        # Page numbers
        page_num_matches = re.findall(r'\b\d+\b', text)
        patterns.extend([f" {num} " for num in page_num_matches])

        # Common header/footer phrases (customize as needed)
        common_patterns = [
            r'Page \d+',
            r'^\d+$',  # Standalone numbers
            r'© \d{4}',  # Copyright
            r'Confidential',
            r'Draft',
        ]

        for pattern in common_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                patterns.append(re.search(pattern, text, re.IGNORECASE).group())

        return patterns

    def _filter_single_page(self, page_text: str, page_num: int, total_pages: int) -> str:
        """Filter headers and footers from a single page."""
        lines = page_text.split('\n')
        if len(lines) < 3:
            return page_text  # Too short to filter

        # Remove header lines (first few lines)
        filtered_lines = self._remove_pattern_lines(lines[:5], self.header_patterns, is_header=True)

        # Remove footer lines (last few lines)
        footer_start = max(len(filtered_lines) - 5, 0)
        filtered_lines = self._remove_pattern_lines(filtered_lines[footer_start:], self.footer_patterns, is_header=False)

        return '\n'.join(filtered_lines)

    def _remove_pattern_lines(self, lines: List[str], patterns: List[str], is_header: bool) -> List[str]:
        """Remove lines that match header/footer patterns."""
        if not patterns:
            return lines

        filtered = []
        for line in lines:
            line_text = line.strip()
            if not line_text:
                continue

            # Check if line matches any pattern
            should_remove = False
            for pattern in patterns:
                if pattern.lower().strip() in line_text.lower():
                    should_remove = True
                    break

            # Additional heuristics
            if not should_remove:
                # Remove very short lines that look like page numbers
                if len(line_text.split()) <= 2 and re.match(r'^\d+$', line_text.strip()):
                    should_remove = True

            if not should_remove:
                filtered.append(line)

        return filtered if filtered else lines  # Don't return empty result


# Global instances
layout_analyzer = LayoutAnalyzer()
header_footer_filter = HeaderFooterFilter()
