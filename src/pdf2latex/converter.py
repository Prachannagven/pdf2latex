"""
Main converter class that orchestrates PDF parsing and LaTeX generation.
"""

from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger

from .pdf_parser import PDFParser
from .latex_generator import LaTeXGenerator


class PDF2LaTeXConverter:
    """
    Main class for converting PDF documents to LaTeX.
    """
    
    def __init__(self, template: str = 'article', preserve_images: bool = True, 
                 config: Optional[Dict[str, Any]] = None):
        """
        Initialize the converter.
        
        Args:
            template: LaTeX document template (article, report, book)
            preserve_images: Whether to include images in the output
            config: Additional configuration options
        """
        self.template = template
        self.preserve_images = preserve_images
        self.config = config or {}
        
        # Initialize components
        self.pdf_parser = PDFParser(config=self.config)
        self.latex_generator = LaTeXGenerator(
            template=template,
            preserve_images=preserve_images,
            config=self.config,
            output_dir=None  # Will be set when we know the output path
        )
        
        logger.info(f"Initialized PDF2LaTeXConverter with template: {template}")
    
    def parse_pdf(self, pdf_path: Path) -> Dict[str, Any]:
        """
        Parse a PDF document and extract content.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Parsed document structure
        """
        logger.info(f"Parsing PDF: {pdf_path}")
        
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        if not pdf_path.suffix.lower() == '.pdf':
            raise ValueError(f"Input file must be a PDF: {pdf_path}")
        
        # Parse the PDF using the PDF parser
        document = self.pdf_parser.parse(pdf_path)
        
        logger.info(f"Successfully parsed PDF with {document.get('page_count', 0)} pages")
        return document
    
    def generate_latex(self, document: Dict[str, Any]) -> str:
        """
        Generate LaTeX code from parsed document.
        
        Args:
            document: Parsed document structure
            
        Returns:
            LaTeX source code
        """
        logger.info("Generating LaTeX code")
        
        # Generate LaTeX using the LaTeX generator
        latex_content = self.latex_generator.generate(document)
        
        logger.info(f"Generated LaTeX code ({len(latex_content)} characters)")
        return latex_content
    
    def convert(self, pdf_path: Path, output_path: Path) -> None:
        """
        Convert PDF to LaTeX in one step.
        
        Args:
            pdf_path: Path to input PDF file
            output_path: Path to output LaTeX file
        """
        logger.info(f"Converting {pdf_path} to {output_path}")
        
        # Update image processor output directory if needed
        if self.preserve_images and self.latex_generator.image_processor:
            image_dir = output_path.parent / f"{output_path.stem}_images"
            self.latex_generator.image_processor.output_dir = image_dir
            image_dir.mkdir(exist_ok=True)
        
        # Parse PDF
        document = self.parse_pdf(pdf_path)
        
        # Generate LaTeX
        latex_content = self.generate_latex(document)
        
        # Write output
        output_path.write_text(latex_content, encoding='utf-8')
        
        logger.info(f"Conversion completed: {output_path}")
        
        # Log image extraction results
        if self.preserve_images and self.latex_generator.image_processor:
            image_count = len(list(self.latex_generator.image_processor.output_dir.glob("*")))
            if image_count > 0:
                logger.info(f"Extracted {image_count} images to: {self.latex_generator.image_processor.output_dir}")
    
    def get_supported_features(self) -> Dict[str, bool]:
        """
        Get information about supported features.
        
        Returns:
            Dictionary of feature names and support status
        """
        return {
            'text_extraction': True,
            'basic_formatting': True,
            'images': self.preserve_images,
            'tables': False,  # Will be implemented later
            'mathematical_expressions': False,  # Will be implemented later
            'bibliography': False,  # Will be implemented later
        }
