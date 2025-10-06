"""
LaTeX generation module for converting parsed PDF content to LaTeX source code.
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import re
from loguru import logger


class LaTeXGenerator:
    """
    Generator that converts parsed PDF content to LaTeX source code.
    """
    
    def __init__(self, template: str = 'article', preserve_images: bool = True,
                 config: Optional[Dict[str, Any]] = None):
        """
        Initialize the LaTeX generator.
        
        Args:
            template: LaTeX document template (article, report, book)
            preserve_images: Whether to include images
            config: Additional configuration options
        """
        self.template = template
        self.preserve_images = preserve_images
        self.config = config or {}
        
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
        
        # Title and author from metadata
        metadata = document.get('metadata', {})
        if metadata.get('title'):
            title = self._escape_latex(metadata['title'])
            preamble_parts.append(f"\\title{{{title}}}")
        
        if metadata.get('author'):
            author = self._escape_latex(metadata['author'])
            preamble_parts.append(f"\\author{{{author}}}")
        
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
        
        if metadata.get('title') or metadata.get('author'):
            return "\\maketitle"
        
        return ""
    
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
        
        # For now, we'll process all pages as a continuous document
        # Later we can add more sophisticated structure detection
        
        for page_num, page in enumerate(pages, 1):
            logger.debug(f"Processing page {page_num}")
            
            page_text = page.get('text', '')
            if page_text.strip():
                # Clean and format the text
                formatted_text = self._format_text(page_text)
                
                if formatted_text.strip():
                    content_parts.append(formatted_text)
            
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
        
        # Escape LaTeX special characters
        text = self._escape_latex(text)
        
        # Split into paragraphs
        paragraphs = text.split('\n\n')
        formatted_paragraphs = []
        
        for paragraph in paragraphs:
            # Clean up whitespace
            cleaned = re.sub(r'\s+', ' ', paragraph.strip())
            
            if cleaned:
                # Simple heuristics for structure detection
                if self._looks_like_heading(cleaned):
                    # Format as section heading
                    heading_text = cleaned.rstrip('.')
                    formatted_paragraphs.append(f"\\section{{{heading_text}}}")
                elif self._looks_like_subheading(cleaned):
                    # Format as subsection heading
                    heading_text = cleaned.rstrip('.')
                    formatted_paragraphs.append(f"\\subsection{{{heading_text}}}")
                else:
                    # Regular paragraph
                    formatted_paragraphs.append(cleaned)
        
        return '\n\n'.join(formatted_paragraphs)
    
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
        }
        
        for char, escaped in latex_special_chars.items():
            result = result.replace(char, escaped)
        
        return result
    
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
