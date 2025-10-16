#!/usr/bin/env python3
"""
Test for word boundary fix in mathematical function detection.
"""

import pytest
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pdf2latex.math_processor import MathProcessor
from pdf2latex.latex_generator import LaTeXGenerator


class TestWordBoundaryMathDetection:
    """Test cases for word boundary fix in math detection."""
    
    def setup_method(self):
        """Set up test cases."""
        self.processor = MathProcessor()
        self.generator = LaTeXGenerator(template='article')
    
    def test_math_functions_within_words_not_detected(self):
        """Test that math function names within words are not detected as math."""
        non_math_texts = [
            "using pdf2latex converter",          # 'sin' within 'using'
            "business logic implementation",      # 'sin' within 'business'
            "processing exponential data",        # 'exp' within 'exponential'
            "costuming and design",              # 'cos' within 'costuming'
            "tangent to the discussion",         # 'tan' within 'tangent'
            "blogging about technology",         # 'log' within 'blogging'
            "lunch time meeting",                # 'ln' within 'lunch'
            "missing file error",                # 'sin' within 'missing'
            "expressing our thoughts",           # 'exp' within 'expressing'
            "according to the manual",           # 'cos' within 'according'
        ]
        
        for text in non_math_texts:
            is_math = self.processor.is_likely_math_line(text)
            assert not is_math, f"Text with function name within word incorrectly detected as math: '{text}'"
    
    def test_actual_math_functions_still_detected(self):
        """Test that actual mathematical functions are still detected."""
        math_texts = [
            "sin(x) = 0.5",
            "cos(θ) + sin(θ) = 1", 
            "tan(45°) = 1",
            "log(x) + ln(y)",
            "exp(x) = e^x",
            "Calculate sin( π/2 )",              # with space before parenthesis
            "The function cos(2x) is periodic",
            "Using tan(α) in trigonometry",
            "Natural log ln(e) = 1",
            "Exponential exp(0) = 1",
        ]
        
        for text in math_texts:
            is_math = self.processor.is_likely_math_line(text)
            assert is_math, f"Actual mathematical function not detected: '{text}'"
    
    def test_hello_world_specific_case(self):
        """Test the specific hello world case that was problematic."""
        problematic_text = "Hello World Anant Kumar October 13, 2025 Hello world! This is a test document to invert using pdf2latex. 1"
        
        # Should not be detected as math
        is_math = self.processor.is_likely_math_line(problematic_text)
        assert not is_math, f"Hello world text incorrectly detected as math: '{problematic_text}'"
        
        # Should not be wrapped in math mode
        formatted = self.generator._format_text(problematic_text)
        assert not (formatted.startswith('$') and formatted.endswith('$')), \
            f"Hello world text incorrectly wrapped in math: '{formatted}'"
    
    def test_mixed_content_with_function_words(self):
        """Test mixed content that contains function names in different contexts."""
        test_cases = [
            ("We are using sin(x) in our calculations", True),    # Actual function usage
            ("We are using advanced algorithms", False),          # Function name within word
            ("The business sin(θ) represents angle", True),       # Mixed: word + function  
            ("The business logic needs improvement", False),      # Only function name within word
        ]
        
        for text, should_be_math in test_cases:
            is_math = self.processor.is_likely_math_line(text)
            if should_be_math:
                assert is_math, f"Mixed text with actual function should be math: '{text}'"
            else:
                assert not is_math, f"Mixed text with function within word should not be math: '{text}'"
    
    def test_text_processing_pipeline_integration(self):
        """Test that the complete text processing pipeline works correctly."""
        test_document = {
            'metadata': {'title': 'Test Document'},
            'pages': [{
                'text': '''Introduction

This document discusses various topics including:
- Using advanced algorithms for processing
- Business logic implementation strategies  
- Processing exponential growth in data
- According to recent studies

Mathematical Analysis

The function sin(x) represents periodic behavior.
We calculate cos(θ) for angular measurements.
The exponential exp(x) grows rapidly.''',
                'page_number': 1
            }],
            'page_count': 1
        }
        
        # Generate LaTeX
        latex_output = self.generator.generate(test_document)
        
        # Verify that regular text with function names within words is not wrapped in math
        assert 'Using advanced algorithms' in latex_output
        assert 'Business logic implementation' in latex_output
        assert 'Processing exponential growth' in latex_output
        assert 'According to recent studies' in latex_output
        
        # Verify that none of these are wrapped in math mode in problematic ways
        lines = latex_output.split('\n')
        for line in lines:
            # Check for obvious math wrapping of regular sentences
            if 'Using advanced algorithms' in line:
                assert not (line.strip().startswith('$') and line.strip().endswith('$'))
            if 'Business logic implementation' in line:
                assert not (line.strip().startswith('$') and line.strip().endswith('$'))


if __name__ == '__main__':
    # Run the tests
    test_class = TestWordBoundaryMathDetection()
    test_class.setup_method()
    
    print("🧪 Testing Word Boundary Math Detection Fix")
    print("=" * 60)
    
    try:
        test_class.test_math_functions_within_words_not_detected()
        print("✅ Math functions within words: PASSED")
        
        test_class.test_actual_math_functions_still_detected()
        print("✅ Actual math functions detection: PASSED")
        
        test_class.test_hello_world_specific_case()
        print("✅ Hello world specific case: PASSED")
        
        test_class.test_mixed_content_with_function_words()
        print("✅ Mixed content handling: PASSED")
        
        test_class.test_text_processing_pipeline_integration()
        print("✅ Text processing pipeline integration: PASSED")
        
        print("\n🎉 All word boundary math detection tests passed!")
        print("\nThe fix correctly:")
        print("  • Prevents false detection of function names within words")
        print("  • Still detects actual mathematical functions")
        print("  • Fixes the hello world specific issue")
        print("  • Works properly in the full text processing pipeline")
        
    except AssertionError as e:
        print(f"❌ Test failed: {e}")
    except Exception as e:
        print(f"❌ Error running tests: {e}")
