"""
Metadata extraction module for enhanced title, author, and date detection.
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from loguru import logger
from datetime import datetime


class MetadataExtractor:
    """
    Enhanced metadata extractor for PDF documents.
    """
    
    def __init__(self):
        """Initialize the metadata extractor."""
        # Patterns for detecting titles in document content
        self.title_patterns = [
            # Common title formatting patterns (newline terminated)
            r'^([A-Z][^.\n]{10,80})(?:\n|$)',
            # Centered text patterns
            r'^\s*([A-Z][A-Za-z\s\-:]{10,80})\s*$',
            # Title-like text at start (more restrictive - stops at common separators)
            r'^([A-Z][A-Za-z\s\-:]{5,50})(?=\s+[A-Z][a-z]+\s+[A-Z][a-z]+|\s+\d{1,2}[/-]\d|\s+(?:January|February|March|April|May|June|July|August|September|October|November|December))',
            # Bold or emphasized text (detected by font analysis)
            r'([A-Z][A-Za-z\s\-:]{10,80})',
        ]
        
        # Patterns for detecting authors
        self.author_patterns = [
            # "By Author Name" patterns - more flexible
            r'(?i)(?:by|written by)[:,]?\s*([A-Z][a-zA-Z.]+(?:\s+[A-Z][a-zA-Z.]+)+)',
            # "Author:" patterns
            r'(?i)author[:,]\s*([A-Z][a-zA-Z.]+(?:\s+[A-Z][a-zA-Z.]+)+(?:\s+and\s+[A-Z][a-zA-Z.]+(?:\s+[A-Z][a-zA-Z.]+)+)*)',
            # Dr./Prof. patterns at start of line
            r'(?i)^\s*((?:Dr\.?|Prof\.?|Professor)\s+[A-Z][a-zA-Z.]+(?:\s+[A-Z][a-zA-Z.]+)*)',
            # Multiple authors with "and"
            r'\b([A-Z][a-zA-Z.]+(?:\s+[A-Z][a-zA-Z.]+)+(?:\s+and\s+[A-Z][a-zA-Z.]+(?:\s+[A-Z][a-zA-Z.]+)+)+)',
            # Email pattern (often indicates author)
            r'([A-Z][a-zA-Z.]+(?:\s+[A-Z][a-zA-Z.]+)+).*?@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            # Institution affiliation pattern  
            r'([A-Z][a-zA-Z.]+(?:\s+[A-Z][a-zA-Z.]+)+).*?(?:University|Institute|College|Department)',
        ]
        
        # Patterns for detecting dates
        self.date_patterns = [
            # Full date formats
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{4})',
            r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})',
            r'((?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4})',
            r'(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})',
            # Month and year only
            r'((?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})',
            # Year only
            r'(?:©|\(c\)|copyright)?\s*(\d{4})',
            r'(?:published|created|updated)[:]\s*(\d{4})',
        ]
        
        # Common academic/document keywords that help identify content structure
        self.structure_keywords = {
            'abstract': r'(?i)\babstract\b',
            'introduction': r'(?i)\b(?:introduction|overview)\b',
            'conclusion': r'(?i)\b(?:conclusion|summary|final)\b',
            'references': r'(?i)\b(?:references|bibliography|works cited)\b',
        }
        
        logger.info("Initialized MetadataExtractor")
    
    def extract_enhanced_metadata(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract enhanced metadata from a parsed document.
        
        Args:
            document: Parsed document structure
            
        Returns:
            Enhanced metadata dictionary
        """
        logger.info("Extracting enhanced metadata")
        
        # Start with existing metadata
        metadata = document.get('metadata', {}).copy()
        
        # Get document text for content analysis
        full_text = self._get_document_text(document)
        first_page_text = self._get_first_page_text(document)
        
        # Extract title if not present or improve existing
        if not metadata.get('title') or len(metadata.get('title', '').strip()) < 3:
            detected_title = self._detect_title(first_page_text, full_text, document)
            if detected_title:
                metadata['title'] = detected_title
                logger.info(f"Detected title: {detected_title}")
        
        # Extract author if not present
        if not metadata.get('author'):
            detected_author = self._detect_author(first_page_text, full_text)
            if detected_author:
                metadata['author'] = detected_author
                logger.info(f"Detected author: {detected_author}")
        
        # Extract date from content (prioritize content over metadata)
        detected_date = self._detect_date(first_page_text, full_text)
        if detected_date:
            metadata['date'] = detected_date
            logger.info(f"Detected date: {detected_date}")
        elif not metadata.get('creation_date') and not metadata.get('date'):
            # Only fallback to empty if no content date and no metadata date
            pass
        
        # Extract document structure information
        structure_info = self._analyze_document_structure(full_text)
        metadata['structure'] = structure_info
        
        # Add content-based quality score
        metadata['quality_score'] = self._calculate_quality_score(metadata, document)
        
        return metadata
    
    def _get_document_text(self, document: Dict[str, Any]) -> str:
        """Get all text content from the document."""
        text_parts = []
        for page in document.get('pages', []):
            if page.get('text'):
                text_parts.append(page['text'])
        return '\n\n'.join(text_parts)
    
    def _get_first_page_text(self, document: Dict[str, Any]) -> str:
        """Get text content from the first page."""
        pages = document.get('pages', [])
        if pages:
            return pages[0].get('text', '')
        return ''
    
    def _detect_title(self, first_page_text: str, full_text: str, document: Dict[str, Any]) -> Optional[str]:
        """
        Detect document title using various heuristics.
        
        Args:
            first_page_text: Text from the first page
            full_text: Full document text
            document: Complete document structure
            
        Returns:
            Detected title or None
        """
        candidates = []
        
        # Method 1: Look for largest text on first page using font information
        title_from_fonts = self._detect_title_from_fonts(document)
        if title_from_fonts:
            candidates.append((title_from_fonts, 10))  # High confidence
        
        # Method 2: Look for text patterns typical of titles
        lines = first_page_text.split('\n')[:10]  # Check first 10 lines
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line or len(line) < 5:
                continue
            
            # Skip lines that look like headers/footers
            if re.search(r'page\s+\d+|^\d+$|^[ivxlc]+$', line.lower()):
                continue
            
            # Look for title-like characteristics
            score = 0
            
            # Length-based scoring (titles are usually 10-80 characters)
            if 10 <= len(line) <= 80:
                score += 3
            elif len(line) > 80:
                score -= 2
            
            # Position-based scoring (earlier is better)
            if i <= 2:
                score += 3
            elif i <= 5:
                score += 1
            
            # Content-based scoring
            if re.match(r'^[A-Z][A-Za-z\s\-:]+$', line):  # Proper case
                score += 2
            if ':' in line and line.count(':') == 1:  # Subtitle pattern
                score += 2
            if line.isupper() and len(line) > 15:  # All caps (common for titles)
                score += 1
            if not re.search(r'\d{4}|\w+@\w+', line):  # No years or emails
                score += 1
            
            if score >= 4:
                candidates.append((line, score))
        
        # Method 3: Look for common title patterns
        for pattern in self.title_patterns:
            matches = re.finditer(pattern, first_page_text, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                candidate = match.group(1).strip()
                if 10 <= len(candidate) <= 100:
                    candidates.append((candidate, 5))
        
        # Select best candidate
        if candidates:
            # Sort by score (descending) and select best
            candidates.sort(key=lambda x: x[1], reverse=True)
            best_title = candidates[0][0]
            
            # Clean up the title
            best_title = re.sub(r'\s+', ' ', best_title)  # Normalize whitespace
            best_title = best_title.strip()
            
            return best_title
        
        return None
    
    def _detect_title_from_fonts(self, document: Dict[str, Any]) -> Optional[str]:
        """
        Detect title based on font size analysis (PyMuPDF only).
        
        Args:
            document: Complete document structure
            
        Returns:
            Title detected from font analysis or None
        """
        if not document.get('pages') or document.get('parser_used') != 'pymupdf':
            return None
        
        first_page = document['pages'][0]
        text_dict = first_page.get('text_dict')
        
        if not text_dict or 'blocks' not in text_dict:
            return None
        
        # Analyze font sizes and find largest text
        font_analysis = []
        
        for block in text_dict['blocks']:
            if 'lines' not in block:
                continue
            
            for line in block['lines']:
                if 'spans' not in line:
                    continue
                
                for span in line['spans']:
                    text = span.get('text', '').strip()
                    font_size = span.get('size', 0)
                    font_flags = span.get('flags', 0)
                    
                    if text and len(text) > 5:
                        is_bold = bool(font_flags & 2**4)  # Bold flag
                        font_analysis.append({
                            'text': text,
                            'size': font_size,
                            'is_bold': is_bold,
                            'bbox': span.get('bbox', [0, 0, 0, 0])
                        })
        
        if not font_analysis:
            return None
        
        # Find text with largest font size
        font_analysis.sort(key=lambda x: x['size'], reverse=True)
        
        # Look for title candidates in top 20% of font sizes
        max_size = font_analysis[0]['size']
        size_threshold = max_size * 0.8
        
        title_candidates = []
        for item in font_analysis:
            if item['size'] >= size_threshold:
                text = item['text']
                # Filter out short texts and page numbers
                if len(text) >= 10 and not re.match(r'^\d+$', text.strip()) and item['bbox'][1] < 200:  # Top area
                    title_candidates.append(text)
        
        if title_candidates:
            # Return the first (largest) suitable candidate
            return title_candidates[0]
        
        return None
    
    def _detect_author(self, first_page_text: str, full_text: str) -> Optional[str]:
        """
        Detect document author using various patterns.
        
        Args:
            first_page_text: Text from the first page
            full_text: Full document text
            
        Returns:
            Detected author or None
        """
        candidates = []
        
        # Search in first page with higher priority
        search_texts = [(first_page_text, 2), (full_text[:2000], 1)]  # Weight first page higher
        
        for text, weight in search_texts:
            # Split into lines for better pattern matching
            lines = text.split('\n')
            
            for pattern in self.author_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    author = match.group(1).strip()
                    # Basic validation for author names
                    if self._is_valid_author_name(author):
                        candidates.append((author, weight))
            
            # Look for lines that might be author names with "By" prefix
            by_pattern = r'(?i)^by\s+(.+)$'
            for line in lines[:10]:
                line = line.strip()
                by_match = re.match(by_pattern, line)
                if by_match:
                    potential_author = by_match.group(1).strip()
                    if self._is_valid_author_name(potential_author):
                        candidates.append((potential_author, weight + 2))  # High weight for "By" prefix
            
            # Look for author-like lines (names that look like authors)
            for i, line in enumerate(lines[1:8]):  # Skip first line (likely title), check next 7
                line = line.strip()
                if not line or len(line) < 5:
                    continue
                
                # Skip lines that are too long (likely content, not author)
                if len(line) > 60:
                    continue
                
                # Look for lines with title + name pattern
                if re.match(r'^(?:Dr\.?|Prof\.?|Professor)\s+[A-Z][a-zA-Z.]+(?:\s+[A-Z][a-zA-Z.]+)+\s*$', line, re.IGNORECASE):
                    if self._is_valid_author_name(line):
                        candidates.append((line, weight + 1))
                
                # Look for simple name patterns (First Last, First Middle Last)
                elif re.match(r'^[A-Z][a-zA-Z.]+(?:\s+[A-Z][a-zA-Z.]+){1,3}\s*$', line):
                    if self._is_valid_author_name(line) and not self._looks_like_title(line):
                        candidates.append((line, weight))
        
        if candidates:
            # Sort by weight and return best candidate
            candidates.sort(key=lambda x: x[1], reverse=True)
            return candidates[0][0]
        
        return None
    
    def _detect_date(self, first_page_text: str, full_text: str) -> Optional[str]:
        """
        Detect document date using various patterns.
        
        Args:
            first_page_text: Text from the first page
            full_text: Full document text
            
        Returns:
            Detected date or None
        """
        candidates = []
        
        # Search in first page and beginning of document
        search_texts = [first_page_text, full_text[:1000]]
        
        for text in search_texts:
            for pattern in self.date_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    date_str = match.group(1).strip()
                    if self._is_valid_date(date_str):
                        candidates.append(date_str)
        
        if candidates:
            # Prefer more complete date formats
            candidates.sort(key=len, reverse=True)
            return candidates[0]
        
        return None
    
    def _analyze_document_structure(self, full_text: str) -> Dict[str, Any]:
        """
        Analyze document structure and identify sections.
        
        Args:
            full_text: Full document text
            
        Returns:
            Structure analysis results
        """
        structure = {
            'has_abstract': False,
            'has_introduction': False,
            'has_conclusion': False,
            'has_references': False,
            'estimated_type': 'document'
        }
        
        text_lower = full_text.lower()
        
        # Check for common document sections
        for section, pattern in self.structure_keywords.items():
            if re.search(pattern, text_lower):
                structure[f'has_{section}'] = True
        
        # Estimate document type based on structure
        if structure['has_abstract'] and structure['has_references']:
            structure['estimated_type'] = 'academic_paper'
        elif structure['has_introduction'] and structure['has_conclusion']:
            structure['estimated_type'] = 'article'
        elif len(full_text) > 10000:
            structure['estimated_type'] = 'report'
        
        return structure
    
    def _is_valid_author_name(self, name: str) -> bool:
        """Check if a string looks like a valid author name."""
        # Basic validation for author names
        if len(name) < 3 or len(name) > 100:
            return False
        
        # Should contain at least one space (first + last name) or be a title+name
        has_space = ' ' in name
        has_title = name.lower().startswith(('dr.', 'prof.', 'professor'))
        
        if not has_space and not has_title:
            return False
        
        # Should not contain numbers or most special characters (except common ones like periods, hyphens)
        if re.search(r'[0-9@#$%^&*(){}[\]|\\<>+=]', name):
            return False
        
        # Should not be all uppercase or all lowercase (unless it has titles)
        if (name.isupper() or name.islower()) and not has_title:
            return False
        
        # Should not contain common non-name words
        non_name_words = ['university', 'institute', 'department', 'college', 'abstract', 'introduction']
        if any(word in name.lower() for word in non_name_words):
            return False
        
        return True
    
    def _looks_like_title(self, text: str) -> bool:
        """Check if text looks more like a title than an author name."""
        # Titles often contain certain words or patterns
        title_indicators = [
            ':',  # Subtitles
            'analysis', 'study', 'research', 'review', 'approach', 'method',
            'impact', 'effect', 'application', 'system', 'development'
        ]
        
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in title_indicators)
    
    def _is_valid_date(self, date_str: str) -> bool:
        """Check if a string looks like a valid date."""
        # Basic validation for dates
        if len(date_str) < 4:
            return False
        
        # Check if it's a reasonable year (1900-2030)
        year_match = re.search(r'\d{4}', date_str)
        if year_match:
            year = int(year_match.group())
            if not (1900 <= year <= 2030):
                return False
        
        return True
    
    def _calculate_quality_score(self, metadata: Dict[str, Any], document: Dict[str, Any]) -> float:
        """
        Calculate a quality score for the extracted metadata.
        
        Args:
            metadata: Extracted metadata
            document: Complete document structure
            
        Returns:
            Quality score between 0 and 1
        """
        score = 0.0
        max_score = 5.0
        
        # Title quality
        if metadata.get('title'):
            title = metadata['title']
            if len(title) >= 10:
                score += 1.0
            if 10 <= len(title) <= 80:
                score += 0.5
        
        # Author quality
        if metadata.get('author'):
            score += 1.0
        
        # Date quality
        if metadata.get('date') or metadata.get('creation_date'):
            score += 1.0
        
        # Structure quality
        structure = metadata.get('structure', {})
        if structure.get('has_abstract') or structure.get('has_introduction'):
            score += 1.0
        
        # Content length quality
        page_count = document.get('page_count', 0)
        if page_count > 1:
            score += 0.5
        
        return min(score / max_score, 1.0)
