"""
LaTeX generation module for converting parsed PDF content to LaTeX source code.
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import re
from loguru import logger
from .math_processor import MathProcessor
from .image_processor import ImageProcessor


class LaTeXGenerator:
    """
    Generator that converts parsed PDF content to LaTeX source code.
    """
    
    def __init__(self, template: str = 'article', preserve_images: bool = True,
                 config: Optional[Dict[str, Any]] = None, output_dir: Optional[Path] = None):
        """
        Initialize the LaTeX generator.
        
        Args:
            template: LaTeX document template (article, report, book)
            preserve_images: Whether to include images
            config: Additional configuration options
            output_dir: Directory for image output
        """
        self.template = template
        self.preserve_images = preserve_images
        self.config = config or {}
        
        # Initialize processors
        self.math_processor = MathProcessor()
        self.image_processor = ImageProcessor(output_dir) if preserve_images else None
        
        # Template configurations
        self.templates = {
            'article': {
                'documentclass': 'article',
                'packages': ['inputenc', 'fontenc', 'geometry', 'graphicx', 'amsmath', 'amsfonts'],
                'geometry': 'margin=1in'
            },
            'report': {
                'documentclass': 'report',
                'packages': ['inputenc', 'fontenc', 'geometry', 'graphicx', 'amsmath', 'amsfonts'],
                'geometry': 'margin=1in'
            },
            'book': {
                'documentclass': 'book',
                'packages': ['inputenc', 'fontenc', 'geometry', 'graphicx', 'amsmath', 'amsfonts'],
                'geometry': 'margin=1in'
            }
        }
        
        logger.info(f"Initialized LaTeXGenerator with template: {template}")
    
    def _normalize_unicode_characters(self, text: str) -> str:
        """
        Normalize Unicode characters that can cause LaTeX compilation issues.
        
        Args:
            text: Text that may contain problematic Unicode characters
            
        Returns:
            Text with normalized characters
        """
        # Replace Unicode minus sign (U+2212) with ASCII hyphen-minus
        text = text.replace('−', '-')
        
        # Replace other problematic Unicode characters if needed
        # Add more replacements here as needed
        
        return text
    
    def generate(self, document: Dict[str, Any]) -> str:
        """
        Generate LaTeX source code from parsed document.
        
        Args:
            document: Parsed document structure
            
        Returns:
            LaTeX source code
        """
        logger.info("Generating LaTeX document")
        
        # Generate document parts
        preamble = self._generate_preamble(document)
        title_section = self._generate_title_section(document)
        content = self._generate_content(document)
        
        # Combine into full document
        latex_document = f"{preamble}\n\n{title_section}\n\n{content}\n\n\\end{{document}}"
        
        logger.info(f"Generated LaTeX document ({len(latex_document)} characters)")
        return latex_document
    
    def _generate_preamble(self, document: Dict[str, Any]) -> str:
        """
        Generate the LaTeX preamble (document class, packages, settings).
        
        Args:
            document: Parsed document structure
            
        Returns:
            LaTeX preamble
        """
        template_config = self.templates.get(self.template, self.templates['article'])
        
        preamble_parts = []
        
        # Document class
        preamble_parts.append(f"\\documentclass{{{template_config['documentclass']}}}")
        
        # Packages
        for package in template_config['packages']:
            if package == 'inputenc':
                preamble_parts.append("\\usepackage[utf8]{inputenc}")
            elif package == 'fontenc':
                preamble_parts.append("\\usepackage[T1]{fontenc}")
            elif package == 'geometry':
                preamble_parts.append(f"\\usepackage[{template_config['geometry']}]{{geometry}}")
            else:
                preamble_parts.append(f"\\usepackage{{{package}}}")
        
        # Additional packages based on content
        if self.preserve_images:
            preamble_parts.append("\\usepackage{float}")  # For better image positioning
        
        # Title, author, and date from metadata
        metadata = document.get('metadata', {})
        
        # Title
        if metadata.get('title'):
            title = self._escape_latex(metadata['title'])
            preamble_parts.append(f"\\title{{{title}}}")
        else:
            # Use filename as fallback
            pdf_path = document.get('pdf_path', '')
            if pdf_path:
                filename = Path(pdf_path).stem
                preamble_parts.append(f"\\title{{{self._escape_latex(filename)}}}")
        
        # Author
        if metadata.get('author'):
            author = self._escape_latex(metadata['author'])
            preamble_parts.append(f"\\author{{{author}}}")
        
        # Date
        date_value = metadata.get('date') or metadata.get('creation_date')
        if date_value:
            # Clean up date format
            clean_date = self._format_date(date_value)
            if clean_date:
                preamble_parts.append(f"\\date{{{clean_date}}}")
        else:
            # Use today's date as fallback
            preamble_parts.append("\\date{\\today}")
        
        # Begin document
        preamble_parts.append("\\begin{document}")
        
        return '\n'.join(preamble_parts)
    
    def _generate_title_section(self, document: Dict[str, Any]) -> str:
        """
        Generate the title section if metadata is available.
        
        Args:
            document: Parsed document structure
            
        Returns:
            LaTeX title section
        """
        metadata = document.get('metadata', {})
        
        # Always generate maketitle since we now ensure title is always set
        title_parts = ["\\maketitle"]
        
        # Add abstract if document structure suggests it has one
        structure = metadata.get('structure', {})
        if structure.get('has_abstract'):
            # Try to extract abstract from first page
            abstract_text = self._extract_abstract(document)
            if abstract_text:
                title_parts.append("")
                title_parts.append("\\begin{abstract}")
                title_parts.append(self._format_text(abstract_text))
                title_parts.append("\\end{abstract}")
        
        return '\n'.join(title_parts)
    
    def _generate_content(self, document: Dict[str, Any]) -> str:
        """
        Generate the main document content.
        
        Args:
            document: Parsed document structure
            
        Returns:
            LaTeX document content
        """
        content_parts = []
        
        pages = document.get('pages', [])
        
        # Extract images if image processor is available
        extracted_images = {}
        if self.preserve_images and self.image_processor:
            try:
                # Get images from document data or extract from PDF
                pdf_path = document.get('pdf_path')
                if pdf_path:
                    extracted_images = self.image_processor.extract_all_images(Path(pdf_path))
            except Exception as e:
                logger.warning(f"Failed to extract images: {e}")
        
        # Process each page
        for page_num, page in enumerate(pages, 1):
            logger.debug(f"Processing page {page_num}")
            
            page_content = []
            
            # Process text content
            page_text = page.get('text', '')
            if page_text.strip():
                # Remove metadata content from the first page to avoid duplication
                if page_num == 1:
                    page_text = self._remove_metadata_from_text(page_text, document.get('metadata', {}))
                
                formatted_text = self._format_text(page_text)
                if formatted_text.strip():
                    page_content.append(formatted_text)
            
            # Process images for this page
            if self.preserve_images and page_num in extracted_images:
                page_images = extracted_images[page_num]
                for img_info in page_images:
                    # Analyze image placement
                    analysis = self.image_processor.analyze_image_placement(img_info, page_text)
                    
                    if analysis['is_likely_figure']:
                        # Generate figure environment
                        caption = f"Figure from page {page_num}"
                        figure_latex = self.image_processor.generate_latex_figure(
                            img_info, 
                            caption=caption,
                            width_ratio=analysis['width_suggestion'],
                            placement=analysis['placement_suggestion']
                        )
                        page_content.append(figure_latex)
                    elif analysis['is_likely_inline']:
                        # Generate inline image
                        inline_latex = self.image_processor.generate_inline_image(img_info)
                        page_content.append(inline_latex)
            
            # Add processed page content
            if page_content:
                content_parts.extend(page_content)
            
            # Add page break between pages (except for the last page)
            if page_num < len(pages) and content_parts:
                content_parts.append("\\newpage")
        
        return '\n\n'.join(content_parts)
    
    def _format_text(self, text: str) -> str:
        """
        Format and clean text for LaTeX output.
        
        Args:
            text: Raw text from PDF
            
        Returns:
            Formatted LaTeX text
        """
        if not text.strip():
            return ""
        
        # Normalize Unicode characters first
        text = self._normalize_unicode_characters(text)
        
        # Split into paragraphs and process each one
        # (math processing happens within _process_paragraph_with_equations)
        paragraphs = text.split('\n\n')
        formatted_paragraphs = []
        
        for paragraph in paragraphs:
            formatted_paragraph = self._process_paragraph_with_equations(paragraph)
            if formatted_paragraph:
                formatted_paragraphs.append(formatted_paragraph)
        
        return '\n\n'.join(formatted_paragraphs)
    
    def _process_paragraph_with_equations(self, paragraph: str) -> str:
        """
        Process a paragraph that might contain multi-line equations.
        
        Args:
            paragraph: Raw paragraph text
            
        Returns:
            Formatted paragraph with proper equation environments
        """
        if not paragraph.strip():
            return ""
        
        # Split into individual lines
        lines = [line.strip() for line in paragraph.split('\n') if line.strip()]
        
        result_lines = []
        math_group = []
        in_equation = False
        
        for line in lines:
            is_math = self.math_processor.is_likely_math_line(line)
            is_equation_number = re.match(r'^\(\d+\)$', line.strip())  # Pattern like "(1)"
            
            if is_math and not is_equation_number:
                # This is a mathematical line - convert to LaTeX but don't escape
                math_line = self.math_processor.convert_to_latex(line)
                math_group.append(math_line)
                in_equation = True
            elif is_equation_number and in_equation:
                # This is equation numbering - add it to the current group
                math_group.append(line)
                # End the equation group
                raw_content = ' '.join(math_group[:-1])  # All but the number
                equation_content = self._reconstruct_equation(raw_content)
                equation_number = math_group[-1].strip('()')  # Extract number
                result_lines.append(f"\\begin{{equation}}")
                result_lines.append(equation_content)
                result_lines.append(f"\\label{{eq:{equation_number}}}")
                result_lines.append(f"\\end{{equation}}")
                math_group = []
                in_equation = False
            else:
                # Not a math line - finalize any pending math group
                if math_group:
                    for line in lines:
                        is_math = self.math_processor.is_likely_math_line(line)
                        is_equation_number = re.match(r'^\(\d+\)$', line.strip())  # Pattern like "(1)"

                        if is_math and not is_equation_number:
                            math_line = self.math_processor.convert_to_latex(line)
                            math_group.append(math_line)
                            in_equation = True
                        elif is_equation_number and in_equation:
                            math_group.append(line)
                            raw_content = ' '.join(math_group[:-1])
                            equation_content = self._reconstruct_equation(raw_content)
                            equation_number = math_group[-1].strip('()')
                            if len(math_group) > 2:
                                # Multi-line: use align environment
                                align_lines = equation_content.split('\\\\')
                                align_body = ' \\\n'.join([l.strip() for l in align_lines if l.strip()])
                                result_lines.append(f"\\begin{{align}}" )
                                result_lines.append(align_body)
                                result_lines.append(f"\\label{{eq:{equation_number}}}")
                                result_lines.append(f"\\end{{align}}" )
                            else:
                                # Single line: use equation environment
                                result_lines.append(f"\\begin{{equation}}" )
                                result_lines.append(equation_content)
                                result_lines.append(f"\\label{{eq:{equation_number}}}")
                                result_lines.append(f"\\end{{equation}}" )
                            math_group = []
                            in_equation = False
                        else:
                            if math_group:
                                if len(math_group) == 1:
                                    result_lines.append(f"\\[{math_group[0]}\\]")
                                elif len(math_group) > 1:
                                    raw_content = ' '.join(math_group)
                                    equation_content = self._reconstruct_equation(raw_content)
                                    align_lines = equation_content.split('\\\\')
                                    align_body = ' \\\n'.join([l.strip() for l in align_lines if l.strip()])
                                    result_lines.append(f"\\begin{{align}}" )
                                    result_lines.append(align_body)
                                    result_lines.append(f"\\end{{align}}" )
                                math_group = []
                                in_equation = False
                            if self._looks_like_heading(line):
                                heading_text = line.rstrip('.')
                                escaped_heading = self._escape_latex(heading_text)
                                result_lines.append(f"\\section{{{escaped_heading}}}")
                            elif self._looks_like_subheading(line):
                                heading_text = line.rstrip('.')
                                escaped_heading = self._escape_latex(heading_text)
                                result_lines.append(f"\\subsection{{{escaped_heading}}}")
                            else:
                                escaped_line = self._escape_latex(line)
                                result_lines.append(escaped_line)
                    # Handle any remaining math group
                    if math_group:
                        if len(math_group) == 1:
                            result_lines.append(f"\\[{math_group[0]}\\]")
                        elif len(math_group) > 1:
                            raw_content = ' '.join(math_group)
                            equation_content = self._reconstruct_equation(raw_content)
                            align_lines = equation_content.split('\\\\')
                            align_body = ' \\\n'.join([l.strip() for l in align_lines if l.strip()])
                        result_lines.append(f"\\begin{{align}}" )
                        result_lines.append(align_body)
                        result_lines.append(f"\\end{{align}}" )
        
        return '\n'.join(result_lines) if result_lines else ""
    
    def _reconstruct_equation(self, raw_content: str) -> str:
        """
        Reconstruct common equation patterns that get split across lines.
        
        Args:
            raw_content: Raw equation content joined from multiple lines
            
        Returns:
            Reconstructed equation with proper mathematical formatting
        """
        import re
        
        # Pattern 1: Drain current equation - ID = 1 2μnCox W L (VGS-Vth)²
        # Should become: ID = (1/2)μnCox(W/L)(VGS-Vth)²
        drain_current_pattern = r'(I_\{D\})\s*=\s*1\s*2(\\mu_\{n\}\s*C_\{Cox\})\s*W\s*L\s*(\(V_\{G_\{S\}\}\s*[\-]\s*V_\{th\}\)\^?\{?2\}?)'
        
        if re.search(drain_current_pattern, raw_content):
            # Reconstruct drain current equation
            reconstructed = re.sub(
                drain_current_pattern,
                r'\1 = \\frac{1}{2}\2 \\frac{W}{L}\3',
                raw_content
            )
            return reconstructed
        
        # Pattern 2: General pattern for "= 1 2μ" → "= (1/2)μ"
        fraction_pattern = r'=\s*1\s*2(\\mu[^}]*\}?[^}]*\}?)'
        if re.search(fraction_pattern, raw_content):
            reconstructed = re.sub(
                fraction_pattern,
                r'= \\frac{1}{2}\1',
                raw_content
            )
            return reconstructed
        
        # Pattern 3: W L pattern → W/L fraction
        wl_pattern = r'(\\frac\{1\}\{2\}[^}]*\}[^}]*\})\s*W\s*L\s*(\([^)]+\))'
        if re.search(wl_pattern, raw_content):
            reconstructed = re.sub(
                wl_pattern,
                r'\1 \\frac{W}{L}\2',
                raw_content
            )
            return reconstructed
        
        # Return original if no patterns match
        return raw_content
    
    def _looks_like_heading(self, text: str) -> bool:
        """
        Simple heuristic to detect if text looks like a heading.
        
        Args:
            text: Text to analyze
            
        Returns:
            True if text looks like a heading
        """
        # Basic heuristics:
        # - Short text (< 100 characters)
        # - No punctuation at the end or ends with period
        # - Might be all caps or title case
        # - Doesn't contain common paragraph words
        
        if len(text) > 100:
            return False
        
        # Check if it's all uppercase (common for headings)
        if text.isupper() and len(text.split()) <= 8:
            return True
        
        # Check if it's title case and short
        if text.istitle() and len(text.split()) <= 6:
            return True
        
        # Check for numbered sections
        if re.match(r'^\d+\.?\s+[A-Z]', text):
            return True
        
        return False
    
    def _looks_like_subheading(self, text: str) -> bool:
        """
        Simple heuristic to detect if text looks like a subheading.
        
        Args:
            text: Text to analyze
            
        Returns:
            True if text looks like a subheading
        """
        # Similar to heading but less strict
        if len(text) > 80:
            return False
        
        # Check for numbered subsections
        if re.match(r'^\d+\.\d+\.?\s+[A-Z]', text):
            return True
        
        return False
    
    def _escape_latex(self, text: str) -> str:
        """
        Escape special LaTeX characters in text.
        
        Args:
            text: Text to escape
            
        Returns:
            Escaped text
        """
        # Handle backslash first to avoid conflicts
        result = text.replace('\\', r'\textbackslash{}')
        
        # Dictionary of other characters that need to be escaped in LaTeX
        latex_special_chars = {
            '&': r'\&',
            '%': r'\%',
            '$': r'\$',
            '#': r'\#',
            '^': r'\textasciicircum{}',
            '_': r'\_',
            '{': r'\{',
            '}': r'\}',
            '~': r'\textasciitilde{}',
            '²': r'\textasciicircum{}2',  # Unicode superscript 2
            '³': r'\textasciicircum{}3',  # Unicode superscript 3
        }
        
        for char, escaped in latex_special_chars.items():
            result = result.replace(char, escaped)
        
        return result
    
    def _format_date(self, date_str: str) -> Optional[str]:
        """
        Format a date string for LaTeX.
        
        Args:
            date_str: Raw date string
            
        Returns:
            Formatted date string or None
        """
        if not date_str:
            return None
        
        # Clean up common date formats
        date_str = str(date_str).strip()
        
        # Handle PDF creation date format (D:YYYYMMDDHHmmSS) first
        pdf_date_match = re.match(r'D:(\d{4})(\d{2})(\d{2})', date_str)
        if pdf_date_match:
            year, month, day = pdf_date_match.groups()
            return f"{day}/{month}/{year}"
        
        # Remove common prefixes after checking for PDF format
        date_str = re.sub(r'^(created:|updated:)\s*', '', date_str, flags=re.IGNORECASE)
        
        # Handle ISO format (YYYY-MM-DD)
        iso_match = re.match(r'(\d{4})-(\d{2})-(\d{2})', date_str)
        if iso_match:
            year, month, day = iso_match.groups()
            return f"{day}/{month}/{year}"
        
        # Handle US format (MM/DD/YYYY)
        us_match = re.match(r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})', date_str)
        if us_match:
            return date_str  # Keep as-is
        
        # Handle full date strings like "January 15, 2024" - keep as-is if they look complete
        if re.match(r'[A-Za-z]+ \d{1,2},? \d{4}', date_str):
            return date_str
        
        # Handle month year format like "March 2024" - keep as-is
        if re.match(r'[A-Za-z]+ \d{4}', date_str):
            return date_str
        
        # Handle year only (fallback)
        year_match = re.search(r'\b(\d{4})\b', date_str)
        if year_match:
            return year_match.group(1)
        
        # Return original if no pattern matches
        return date_str[:50]  # Limit length
    
    def _extract_abstract(self, document: Dict[str, Any]) -> Optional[str]:
        """
        Extract abstract text from the document.
        
        Args:
            document: Parsed document structure
            
        Returns:
            Abstract text or None
        """
        # Get first page text
        pages = document.get('pages', [])
        if not pages:
            return None
        
        first_page_text = pages[0].get('text', '')
        
        # Look for abstract section - more flexible patterns
        abstract_patterns = [
            r'(?i)abstract\s*[:\-]?\s*\n(.+?)(?=\n\s*(?:introduction|overview|1\.|keywords|key words))',
            r'(?i)abstract\s*[:\-]?\s*(.+?)(?=\n\s*(?:introduction|overview|1\.|keywords|key words))',
            r'(?i)summary\s*[:\-]?\s*\n(.+?)(?=\n\s*(?:introduction|overview|1\.))',
        ]
        
        for pattern in abstract_patterns:
            match = re.search(pattern, first_page_text, re.DOTALL)
            if match:
                abstract_text = match.group(1).strip()
                # Clean up the abstract text
                abstract_text = re.sub(r'\s+', ' ', abstract_text)  # Normalize whitespace
                abstract_text = abstract_text[:1000]  # Limit length
                
                if len(abstract_text) > 50:  # Ensure it's substantial
                    return abstract_text
        
        return None
    
    def _escape_latex_preserving_math(self, text: str) -> str:
        """
        Escape LaTeX special characters but preserve math commands.
        
        Args:
            text: Text that may contain LaTeX math commands
            
        Returns:
            Escaped text with math commands preserved
        """
        import uuid
        
        # Find and temporarily replace math commands with placeholders
        math_patterns = [
            r'\\[a-zA-Z]+',  # LaTeX commands like \mu, \frac, etc.
            r'\{[^}]*\}',    # Braces with content
            r'\^{[^}]*}',    # Superscripts
            r'_{[^}]*}',     # Subscripts
            r'\\frac{[^}]*}{[^}]*}',  # Fractions
        ]
        
        placeholders = {}
        result = text
        
        # Replace math patterns with unique placeholders
        for pattern in math_patterns:
            matches = re.finditer(pattern, result)
            for match in reversed(list(matches)):  # Reverse to maintain indices
                placeholder = f"__MATH_PLACEHOLDER_{uuid.uuid4().hex[:8]}__"
                placeholders[placeholder] = match.group()
                result = result[:match.start()] + placeholder + result[match.end():]
        
        # Escape the remaining text
        result = self._escape_latex(result)
        
        # Restore math commands
        for placeholder, original in placeholders.items():
            result = result.replace(placeholder, original)
        
        return result
    
    def _remove_metadata_from_text(self, text: str, metadata: Dict[str, Any]) -> str:
        """
        Remove metadata content from text to avoid duplication in document body.
        
        Args:
            text: Original page text
            metadata: Extracted metadata dictionary
            
        Returns:
            Text with metadata portions removed
        """
        if not text.strip():
            return text
        
        # Get metadata values to look for
        title = (metadata.get('title') or '').strip()
        author = (metadata.get('author') or '').strip()
        date = (metadata.get('date') or '').strip()
        
        # Handle single-line format specially
        if '\n' not in text.strip():
            return self._filter_single_line_metadata(text, title, author, date)
        
        # Handle multi-line format
        lines = text.split('\n')
        filtered_lines = []
        
        for line in lines:
            line_stripped = line.strip()
            
            # Skip empty lines at the beginning (they'll be added back if needed)
            if not line_stripped:
                # Only add empty lines if we already have content
                if filtered_lines:
                    filtered_lines.append(line)
                continue
            
            # Skip lines that match extracted metadata
            skip_line = False
            
            # Check if line matches title
            if title and (line_stripped == title or line_stripped.startswith(title)):
                skip_line = True
            
            # Check if line matches author
            elif author and (line_stripped == author or author in line_stripped):
                # Be more careful with author matching - check if it's a standalone line
                if len(line_stripped) < 100 and author in line_stripped:
                    skip_line = True
            
            # Check if line matches date patterns
            elif date and date in line_stripped:
                skip_line = True
            
            # Also skip lines that are just the author and date combined
            elif author and date and author in line_stripped and date in line_stripped:
                skip_line = True
            
            if not skip_line:
                filtered_lines.append(line)
        
        # Clean up multiple consecutive empty lines
        result_lines = []
        prev_empty = False
        
        for line in filtered_lines:
            is_empty = not line.strip()
            if not (is_empty and prev_empty):  # Don't add consecutive empty lines
                result_lines.append(line)
            prev_empty = is_empty
        
        # Remove leading and trailing empty lines
        while result_lines and not result_lines[0].strip():
            result_lines.pop(0)
        while result_lines and not result_lines[-1].strip():
            result_lines.pop()
        
        return '\n'.join(result_lines)

    def _filter_single_line_metadata(self, text: str, title: str, author: str, date: str) -> str:
        """
        Filter metadata from single-line text format.
        
        Args:
            text: Single line of text
            title: Extracted title
            author: Extracted author  
            date: Extracted date
            
        Returns:
            Text with metadata portions removed
        """
        result = text.strip()
        
        # Remove metadata components in order from start of line
        if title and result.startswith(title):
            result = result[len(title):].strip()
        
        if author and result.startswith(author):
            result = result[len(author):].strip()
        
        # Remove date patterns
        if date:
            # Try exact match first
            if date in result:
                result = result.replace(date, '', 1).strip()
            else:
                # Try removing date components
                # Remove common date patterns
                date_patterns = [
                    r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4}\b',
                    r'\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b',
                    r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',
                    r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b',
                ]
                
                for pattern in date_patterns:
                    result = re.sub(pattern, '', result, flags=re.IGNORECASE).strip()
        
        # Clean up extra whitespace and common separators
        result = re.sub(r'\s+', ' ', result)
        result = re.sub(r'^[,\-\s]+|[,\-\s]+$', '', result)
        
        return result.strip()

    def _generate_image_inclusion(self, image_info: Dict[str, Any], page_num: int) -> str:
        """
        Generate LaTeX code for including an image.
        
        Args:
            image_info: Image information from PDF parser
            page_num: Page number where image appears
            
        Returns:
            LaTeX code for image inclusion
        """
        if not self.preserve_images:
            return ""
        
        # For now, just create a placeholder
        # In a full implementation, we'd extract and save the actual image
        image_filename = f"image_p{page_num}_{image_info.get('index', 0)}"
        
        latex_code = f"""\\begin{{figure}}[H]
    \\centering
    \\includegraphics[width=0.8\\textwidth]{{{image_filename}}}
    \\caption{{Image from page {page_num}}}
    \\label{{fig:p{page_num}_img{image_info.get('index', 0)}}}
\\end{{figure}}"""
        
        return latex_code
