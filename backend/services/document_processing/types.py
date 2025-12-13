from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class PageResult:
    """Result for a single page extraction"""
    page_number: int
    text: str
    method: str  # 'text' or 'ocr'
    confidence: Optional[float] = None
    error: Optional[str] = None
    success: bool = True


@dataclass
class ExtractionResult:
    """Complete extraction result for a PDF"""
    success: bool
    pages: List[PageResult]
    errors: List[Dict[str, Any]]
    stats: Dict[str, int]
    full_text: str

    @property
    def total_pages(self) -> int:
        return self.stats.get('total_pages', 0)

    @property
    def successful_pages(self) -> int:
        return self.stats.get('successful_pages', 0)

    @property
    def failed_pages(self) -> int:
        return self.stats.get('failed_pages', 0)
