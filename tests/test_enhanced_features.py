"""
Tests for enhanced mathematical expression and image processing features.
"""

import pytest
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pdf2latex.math_processor import MathProcessor
from pdf2latex.image_processor import ImageProcessor


class TestMathProcessor:
    """Test the mathematical expression processor."""
    
    def test_math_processor_initialization(self):
        """Test MathProcessor initialization."""
        processor = MathProcessor()
        
        assert processor.patterns is not None
        assert processor.greek_letters is not None
        assert len(processor.greek_letters) > 0
    
    def test_superscript_conversion(self):
        """Test superscript conversion."""
        processor = MathProcessor()
        
        # Unicode superscripts
        assert processor.convert_to_latex("x²") == "x^{2}"
        assert processor.convert_to_latex("E³") == "E^{3}"
        
        # Explicit superscripts
        assert processor.convert_to_latex("x^2") == "x^{2}"
        assert processor.convert_to_latex("E^-1") == "E^{-1}"
    
    def test_subscript_conversion(self):
        """Test subscript conversion."""
        processor = MathProcessor()
        
        # Unicode subscripts
        assert processor.convert_to_latex("H₂O") == "H_{2}O"
        assert processor.convert_to_latex("CO₂") == "CO_{2}"
        
        # Explicit subscripts
        assert processor.convert_to_latex("x_i") == "x_{i}"
        assert processor.convert_to_latex("a_1") == "a_{1}"
    
    def test_fraction_conversion(self):
        """Test fraction conversion."""
        processor = MathProcessor()
        
        assert processor.convert_to_latex("1/2") == "\\frac{1}{2}"
        assert processor.convert_to_latex("3/4") == "\\frac{3}{4}"
        assert processor.convert_to_latex("(x+1)/(x-1)") == "\\frac{x+1}{x-1}"
    
    def test_greek_letters(self):
        """Test Greek letter conversion."""
        processor = MathProcessor()
        
        # Test that Greek letters are converted (the actual output depends on LaTeX escaping)
        result_alpha = processor.convert_to_latex("α")
        assert "alpha" in result_alpha
        result_beta = processor.convert_to_latex("β")
        assert "beta" in result_beta
        result_pi = processor.convert_to_latex("π")
        assert "pi" in result_pi
        result_omega = processor.convert_to_latex("Ω")
        assert "Omega" in result_omega
    
    def test_mathematical_operators(self):
        """Test mathematical operator conversion."""
        processor = MathProcessor()
        
        assert processor.convert_to_latex("x ≤ y") == "x \\leq y"
        assert processor.convert_to_latex("a ≥ b") == "a \\geq b"
        assert processor.convert_to_latex("p ≠ q") == "p \\neq q"
        assert processor.convert_to_latex("≈") == "\\approx"
        assert processor.convert_to_latex("∞") == "\\infty"
    
    def test_math_functions(self):
        """Test mathematical function conversion."""
        processor = MathProcessor()
        
        assert "\\sin(x)" in processor.convert_to_latex("sin(x)")
        result = processor.convert_to_latex("cos(θ)")
        assert "\\cos" in result and "theta" in result
        assert "\\log(10)" in processor.convert_to_latex("log(10)")
        assert "\\ln(e)" in processor.convert_to_latex("ln(e)")
    
    def test_complex_expressions(self):
        """Test complex mathematical expressions."""
        processor = MathProcessor()
        
        # Einstein's equation
        result = processor.convert_to_latex("E = mc²")
        assert "E = mc^{2}" in result
        
        # Pythagorean theorem
        result = processor.convert_to_latex("a² + b² = c²")
        assert "a^{2} + b^{2} = c^{2}" in result
    
    def test_math_line_detection(self):
        """Test mathematical line detection."""
        processor = MathProcessor()
        
        # Should detect as math
        assert processor.is_likely_math_line("E = mc²")
        assert processor.is_likely_math_line("a² + b² = c²")
        assert processor.is_likely_math_line("x ≤ y")
        assert processor.is_likely_math_line("sin(x) = y")
        assert processor.is_likely_math_line("π ≈ 3.14159")
        
        # Should not detect as math
        assert not processor.is_likely_math_line("This is regular text.")
        assert not processor.is_likely_math_line("The quick brown fox jumps.")
    
    def test_expression_detection(self):
        """Test mathematical expression detection."""
        processor = MathProcessor()
        
        text = "The equation E = mc² is famous, and π ≈ 3.14159."
        expressions = processor.detect_math_expressions(text)
        
        assert len(expressions) > 0
        
        # Check that we found some expressions
        found_types = [expr['type'] for expr in expressions]
        assert 'expressions' in found_types or 'superscript' in found_types


class TestImageProcessor:
    """Test the image processing functionality."""
    
    def test_image_processor_initialization(self):
        """Test ImageProcessor initialization."""
        processor = ImageProcessor()
        
        assert processor.output_dir.exists()
        assert processor.supported_formats == {'.png', '.jpg', '.jpeg', '.pdf', '.eps'}
    
    def test_custom_output_directory(self):
        """Test custom output directory creation."""
        custom_dir = Path("test_images")
        processor = ImageProcessor(custom_dir)
        
        assert processor.output_dir == custom_dir
        assert processor.output_dir.exists()
        
        # Cleanup
        custom_dir.rmdir()
    
    def test_generate_latex_figure(self):
        """Test LaTeX figure generation."""
        processor = ImageProcessor()
        
        image_info = {
            'filename': 'test_image.png',
            'page_number': 1,
            'index': 0,
            'width': 400,
            'height': 300
        }
        
        latex_code = processor.generate_latex_figure(image_info)
        
        assert '\\begin{figure}' in latex_code
        assert '\\includegraphics' in latex_code
        assert 'test_image.png' in latex_code
        assert '\\caption' in latex_code
        assert '\\end{figure}' in latex_code
    
    def test_generate_inline_image(self):
        """Test inline image generation."""
        processor = ImageProcessor()
        
        image_info = {
            'filename': 'small_image.png',
            'width': 200,
            'height': 150
        }
        
        latex_code = processor.generate_inline_image(image_info)
        
        assert '\\includegraphics' in latex_code
        assert 'small_image.png' in latex_code
        assert 'width=' in latex_code
    
    def test_image_placement_analysis(self):
        """Test image placement analysis."""
        processor = ImageProcessor()
        
        # Large image
        large_image = {
            'width': 800,
            'height': 600,
            'bbox': None
        }
        
        analysis = processor.analyze_image_placement(large_image, "Sample text")
        
        assert analysis['is_large'] == True
        assert analysis['is_small'] == False
        assert analysis['aspect_ratio'] > 0
        
        # Small image
        small_image = {
            'width': 100,
            'height': 80,
            'bbox': None
        }
        
        analysis = processor.analyze_image_placement(small_image, "Sample text")
        
        assert analysis['is_large'] == False
        assert analysis['is_small'] == True
        assert analysis['is_likely_inline'] == True
    
    def test_document_hash_generation(self):
        """Test document hash generation."""
        processor = ImageProcessor()
        
        # Create a temporary file for testing
        test_file = Path("test_file.pdf")
        test_file.write_text("test content")
        
        hash1 = processor.get_document_hash(test_file)
        hash2 = processor.get_document_hash(test_file)
        
        # Same file should generate same hash
        assert hash1 == hash2
        assert len(hash1) == 8  # Should be 8 character hash
        
        # Cleanup
        test_file.unlink()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
