"""
Basic tests for the PDF to LaTeX converter.
"""

import pytest
from pathlib import Path
import tempfile
import sys
import os

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pdf2latex import PDF2LaTeXConverter


class TestPDF2LaTeXConverter:
    """Test cases for the main converter class."""
    
    def test_converter_initialization(self):
        """Test that the converter initializes correctly."""
        converter = PDF2LaTeXConverter()
        assert converter.template == 'article'
        assert converter.preserve_images == True
        
        converter_custom = PDF2LaTeXConverter(template='report', preserve_images=False)
        assert converter_custom.template == 'report'
        assert converter_custom.preserve_images == False
    
    def test_supported_features(self):
        """Test that supported features are reported correctly."""
        converter = PDF2LaTeXConverter()
        features = converter.get_supported_features()
        
        assert isinstance(features, dict)
        assert 'text_extraction' in features
        assert features['text_extraction'] == True
        assert 'images' in features
        assert features['images'] == True  # Default preserve_images=True


class TestPDFParser:
    """Test cases for the PDF parser."""
    
    def test_parser_initialization(self):
        """Test that the PDF parser initializes correctly."""
        from pdf2latex.pdf_parser import PDFParser
        
        parser = PDFParser()
        assert parser.preferred_library == 'pymupdf'
        
        parser_custom = PDFParser(config={'preferred_library': 'pdfplumber'})
        assert parser_custom.preferred_library == 'pdfplumber'


class TestLaTeXGenerator:
    """Test cases for the LaTeX generator."""
    
    def test_generator_initialization(self):
        """Test that the LaTeX generator initializes correctly."""
        from pdf2latex.latex_generator import LaTeXGenerator
        
        generator = LaTeXGenerator()
        assert generator.template == 'article'
        assert generator.preserve_images == True
    
    def test_escape_latex(self):
        """Test LaTeX character escaping."""
        from pdf2latex.latex_generator import LaTeXGenerator
        
        generator = LaTeXGenerator()
        
        # Test basic escaping
        assert generator._escape_latex("Hello & World") == "Hello \\& World"
        assert generator._escape_latex("100% sure") == "100\\% sure"
        assert generator._escape_latex("$money$") == "\\$money\\$"
        assert generator._escape_latex("C#") == "C\\#"
    
    def test_generate_preamble(self):
        """Test preamble generation."""
        from pdf2latex.latex_generator import LaTeXGenerator
        
        generator = LaTeXGenerator(template='article')
        
        document = {
            'metadata': {
                'title': 'Test Document',
                'author': 'Test Author'
            }
        }
        
        preamble = generator._generate_preamble(document)
        
        assert '\\documentclass{article}' in preamble
        assert '\\title{Test Document}' in preamble
        assert '\\author{Test Author}' in preamble
        assert '\\begin{document}' in preamble
    
    def test_format_text(self):
        """Test text formatting."""
        from pdf2latex.latex_generator import LaTeXGenerator
        
        generator = LaTeXGenerator()
        
        # Test basic text formatting
        text = "This is a test paragraph.\n\nThis is another paragraph."
        formatted = generator._format_text(text)
        
        assert "This is a test paragraph." in formatted
        assert "This is another paragraph." in formatted


if __name__ == '__main__':
    # Run tests
    pytest.main([__file__, '-v'])
