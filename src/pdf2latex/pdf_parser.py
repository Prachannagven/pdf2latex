"""
PDF parsing module using multiple libraries for robust text and structure extraction.
"""

import fitz  # PyMuPDF
import pdfplumber
import PyPDF2
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from loguru import logger
import io


class PDFParser:
    """
    PDF parser that uses multiple libraries to extract content from PDF files.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the PDF parser.
        
        Args:
            config: Configuration options
        """
        self.config = config or {}
        self.preferred_library = self.config.get('preferred_library', 'pymupdf')
        
        logger.info(f"Initialized PDFParser with preferred library: {self.preferred_library}")
    
    def parse(self, pdf_path: Path) -> Dict[str, Any]:
        """
        Parse a PDF file and extract content.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary containing parsed content
        """
        logger.info(f"Parsing PDF: {pdf_path}")
        
        # Try different parsing strategies
        strategies = [
            ('pymupdf', self._parse_with_pymupdf),
            ('pdfplumber', self._parse_with_pdfplumber),
            ('pypdf2', self._parse_with_pypdf2)
        ]
        
        # Start with preferred library if specified
        if self.preferred_library:
            strategies = [(lib, func) for lib, func in strategies if lib == self.preferred_library] + \
                        [(lib, func) for lib, func in strategies if lib != self.preferred_library]
        
        last_error = None
        for library_name, parse_func in strategies:
            try:
                logger.info(f"Attempting to parse with {library_name}")
                result = parse_func(pdf_path)
                if result and result.get('pages'):
                    logger.info(f"Successfully parsed with {library_name}")
                    result['parser_used'] = library_name
                    return result
            except Exception as e:
                logger.warning(f"Failed to parse with {library_name}: {e}")
                last_error = e
                continue
        
        # If all strategies failed
        raise RuntimeError(f"Failed to parse PDF with any available library. Last error: {last_error}")
    
    def _parse_with_pymupdf(self, pdf_path: Path) -> Dict[str, Any]:
        """
        Parse PDF using PyMuPDF (fitz).
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Parsed document structure
        """
        doc = fitz.open(pdf_path)
        
        document = {
            'metadata': {
                'title': doc.metadata.get('title', ''),
                'author': doc.metadata.get('author', ''),
                'subject': doc.metadata.get('subject', ''),
                'creator': doc.metadata.get('creator', ''),
                'producer': doc.metadata.get('producer', ''),
                'creation_date': doc.metadata.get('creationDate', ''),
                'modification_date': doc.metadata.get('modDate', ''),
            },
            'page_count': len(doc),
            'pages': []
        }
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # Extract text
            text = page.get_text()
            
            # Extract text with formatting information
            text_dict = page.get_text("dict")
            
            # Extract images
            images = []
            image_list = page.get_images()
            for img_index, img in enumerate(image_list):
                xref = img[0]
                pix = fitz.Pixmap(doc, xref)
                if pix.n - pix.alpha < 4:  # GRAY or RGB
                    images.append({
                        'index': img_index,
                        'xref': xref,
                        'width': pix.width,
                        'height': pix.height,
                        'colorspace': pix.colorspace.name if pix.colorspace else 'unknown',
                        'size': len(pix.tobytes())
                    })
                pix = None
            
            page_data = {
                'page_number': page_num + 1,
                'text': text,
                'text_dict': text_dict,
                'images': images,
                'bbox': page.rect,
                'rotation': page.rotation
            }
            
            document['pages'].append(page_data)
        
        doc.close()
        return document
    
    def _parse_with_pdfplumber(self, pdf_path: Path) -> Dict[str, Any]:
        """
        Parse PDF using pdfplumber.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Parsed document structure
        """
        with pdfplumber.open(pdf_path) as pdf:
            document = {
                'metadata': pdf.metadata or {},
                'page_count': len(pdf.pages),
                'pages': []
            }
            
            for page_num, page in enumerate(pdf.pages):
                # Extract text
                text = page.extract_text() or ""
                
                # Extract words with positions
                words = page.extract_words()
                
                # Extract tables
                tables = page.extract_tables()
                
                # Extract images
                images = []
                if hasattr(page, 'images'):
                    images = [{
                        'bbox': img['bbox'],
                        'width': img.get('width', 0),
                        'height': img.get('height', 0)
                    } for img in page.images]
                
                page_data = {
                    'page_number': page_num + 1,
                    'text': text,
                    'words': words,
                    'tables': tables,
                    'images': images,
                    'bbox': page.bbox,
                    'width': page.width,
                    'height': page.height
                }
                
                document['pages'].append(page_data)
        
        return document
    
    def _parse_with_pypdf2(self, pdf_path: Path) -> Dict[str, Any]:
        """
        Parse PDF using PyPDF2.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Parsed document structure
        """
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            document = {
                'metadata': dict(pdf_reader.metadata) if pdf_reader.metadata else {},
                'page_count': len(pdf_reader.pages),
                'pages': []
            }
            
            for page_num, page in enumerate(pdf_reader.pages):
                # Extract text
                text = page.extract_text()
                
                page_data = {
                    'page_number': page_num + 1,
                    'text': text,
                    'mediabox': page.mediabox,
                    'rotation': page.get('/Rotate', 0)
                }
                
                document['pages'].append(page_data)
        
        return document
    
    def get_text_content(self, document: Dict[str, Any]) -> str:
        """
        Extract all text content from a parsed document.
        
        Args:
            document: Parsed document structure
            
        Returns:
            Combined text content
        """
        text_parts = []
        for page in document.get('pages', []):
            if page.get('text'):
                text_parts.append(page['text'])
        
        return '\n\n'.join(text_parts)
    
    def get_page_text(self, document: Dict[str, Any], page_num: int) -> str:
        """
        Get text content from a specific page.
        
        Args:
            document: Parsed document structure
            page_num: Page number (1-based)
            
        Returns:
            Text content of the specified page
        """
        pages = document.get('pages', [])
        if 1 <= page_num <= len(pages):
            return pages[page_num - 1].get('text', '')
        return ''
