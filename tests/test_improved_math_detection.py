#!/usr/bin/env python3
"""
Test for improved mathematical expression detection - ensuring regular text isn't treated as math.
"""

import pytest
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pdf2latex.math_processor import MathProcessor
from pdf2latex.latex_generator import LaTeXGenerator


class TestImprovedMathDetection:
    """Test cases for improved mathematical expression detection."""
    
    def setup_method(self):
        """Set up test cases."""
        self.processor = MathProcessor()
        self.generator = LaTeXGenerator(template='article')
    
    def test_false_positive_prevention(self):
        """Test that regular text is not incorrectly identified as mathematical."""
        non_math_texts = [
            "The survey showed a 85% response rate among participants.",
            "Statistical significance was found (p < 0.05) for the primary outcome.",
            "Please see Chapter 3.4 for detailed analysis of the results.",
            "The algorithm processes data in O(n²) time complexity.",
            "Version 2.1.3 includes bug fixes and performance improvements.",
            "Price range: $15.99 - $29.99 depending on configuration.",
            "The temperature was 25°C yesterday.",
            "Contact phone: 555-1234 or email: support@company.com",
            "Meeting scheduled for 2:30 PM in Room 101A.",
            "The coefficient β was significant in the analysis.",
            "Variables a, b, and c were analyzed in different contexts."
        ]
        
        for text in non_math_texts:
            is_math = self.processor.is_likely_math_line(text)
            assert not is_math, f"Text incorrectly identified as math: '{text}'"
    
    def test_true_positive_preservation(self):
        """Test that actual mathematical expressions are still detected."""
        math_texts = [
            "E = mc²",
            "a² + b² = c²", 
            "f(x) = x² + 2x + 1",
            "∫ sin(x) dx = -cos(x) + C",
            "∑(i=1 to n) i = n(n+1)/2",
            "x^2 + y^2 = r^2",
            "log(ab) = log(a) + log(b)",
            "√(25) = 5",
            "π ≈ 3.14159",
            "Results with α = 0.05 threshold"  # This one should be detected due to equation context
        ]
        
        for text in math_texts:
            is_math = self.processor.is_likely_math_line(text)
            assert is_math, f"Mathematical text not detected: '{text}'"
    
    def test_contextual_exclusions(self):
        """Test specific contextual exclusions work properly."""
        # Test percentage exclusions
        assert not self.processor.is_likely_math_line("85% response rate among users")
        assert not self.processor.is_likely_math_line("20% increase in revenue")
        
        # Test statistical significance exclusions  
        assert not self.processor.is_likely_math_line("p < 0.05 for primary outcome")
        assert not self.processor.is_likely_math_line("p > 0.01 was found")
        
        # Test time complexity exclusions
        assert not self.processor.is_likely_math_line("O(n²) time complexity")
        assert not self.processor.is_likely_math_line("algorithm runs in O(log n) time")
        
        # Test reference exclusions
        assert not self.processor.is_likely_math_line("see section 3.4 for details")
        assert not self.processor.is_likely_math_line("refer to Chapter 2.1")
        assert not self.processor.is_likely_math_line("version 1.0 was released")
    
    def test_text_processing_pipeline(self):
        """Test that the full text processing pipeline doesn't wrap regular text in math."""
        regular_texts = [
            "This is a normal paragraph with regular content.",
            "The company reported growth in Q3 2024.",
            "Statistical analysis showed p < 0.05 significance.",
            "The survey had 85% response rate.",
            "Algorithm complexity is O(n²) in worst case.",
            "Version 2.1 includes performance improvements."
        ]
        
        for text in regular_texts:
            processed = self.generator._format_text(text)
            
            # Should not be wrapped in math environments
            assert not processed.startswith('$'), f"Text incorrectly wrapped in inline math: '{text}'"
            assert not processed.startswith('\\['), f"Text incorrectly wrapped in display math: '{text}'"
            assert not (processed.startswith('$') and processed.endswith('$')), f"Text incorrectly wrapped in math: '{text}'"
    
    def test_mathematical_text_still_processed(self):
        """Test that actual mathematical expressions are still processed correctly."""
        math_texts = [
            "E = mc²",
            "a² + b² = c²",
            "x^2 + y^2 = r^2"
        ]
        
        for text in math_texts:
            processed = self.generator._format_text(text)
            
            # Should be wrapped in math environment or contain LaTeX math commands
            has_math_wrapping = (processed.startswith('$') and processed.endswith('$')) or \
                               (processed.startswith('\\[') and processed.endswith('\\]')) or \
                               ('\\' in processed)  # Contains LaTeX commands
            
            assert has_math_wrapping, f"Mathematical text not properly processed: '{text}' -> '{processed}'"
    
    def test_mixed_content_handling(self):
        """Test handling of text that contains both regular and mathematical content."""
        mixed_texts = [
            ("The equation E = mc² shows the relationship.", True),  # Should be math due to equation
            ("Using α = 0.05 as threshold for significance.", True),  # Should be math due to equation context
            ("The coefficient β was found to be significant.", False),  # Just mentions Greek letter
            ("Variables a, b, and c were analyzed.", False),  # Just variable names
        ]
        
        for text, should_be_math in mixed_texts:
            is_math = self.processor.is_likely_math_line(text)
            if should_be_math:
                assert is_math, f"Mixed text should be detected as math: '{text}'"
            else:
                assert not is_math, f"Mixed text should not be detected as math: '{text}'"


def test_improved_math_detection_integration():
    """Integration test for the improved math detection system."""
    processor = MathProcessor()
    generator = LaTeXGenerator(template='article')
    
    # Test document with mixed content
    test_document = {
        'metadata': {'title': 'Test Document'},
        'pages': [{
            'text': '''Research Results

Statistical Analysis

The survey showed a 85% response rate among participants.
Statistical significance was found (p < 0.05) for the primary outcome.
The coefficient β was significant in the regression analysis.

Mathematical Equations

The famous equation E = mc² relates energy and mass.
For right triangles: a² + b² = c²
The quadratic formula: x = (-b ± √(b²-4ac)) / 2a

Algorithm Performance

The algorithm processes data in O(n²) time complexity.
Version 2.1 includes performance improvements.
See Chapter 3.4 for detailed analysis.''',
            'page_number': 1
        }],
        'page_count': 1
    }
    
    # Generate LaTeX
    latex_output = generator.generate(test_document)
    
    # Verify that regular text sections aren't wrapped in math
    assert '85\\% response rate' in latex_output
    assert '(p < 0.05)' in latex_output  # Should not be wrapped in math
    assert 'O(n\\textasciicircum' in latex_output  # Complex algorithm notation properly escaped
    
    # Verify that actual equations are handled properly  
    assert 'E = mc' in latex_output  # Part of the Einstein equation
    assert '\\textasciicircum' in latex_output  # Superscripts are properly escaped


if __name__ == '__main__':
    # Run the tests
    test_class = TestImprovedMathDetection()
    test_class.setup_method()
    
    print("🧪 Testing Improved Mathematical Expression Detection")
    print("=" * 60)
    
    try:
        test_class.test_false_positive_prevention()
        print("✅ False positive prevention: PASSED")
        
        test_class.test_true_positive_preservation()
        print("✅ True positive preservation: PASSED")
        
        test_class.test_contextual_exclusions()
        print("✅ Contextual exclusions: PASSED")
        
        test_class.test_text_processing_pipeline()
        print("✅ Text processing pipeline: PASSED")
        
        test_class.test_mathematical_text_still_processed()
        print("✅ Mathematical text processing: PASSED")
        
        test_class.test_mixed_content_handling()
        print("✅ Mixed content handling: PASSED")
        
        test_improved_math_detection_integration()
        print("✅ Integration test: PASSED")
        
        print("\n🎉 All improved math detection tests passed!")
        print("\nThe PDF2LaTeX converter now correctly:")
        print("  • Avoids treating regular text as mathematical expressions")
        print("  • Excludes percentage contexts (85% response rate)")
        print("  • Excludes statistical significance (p < 0.05)")
        print("  • Excludes time complexity notation (O(n²))")
        print("  • Excludes version/section references (Chapter 3.4)")
        print("  • Still detects actual mathematical equations")
        print("  • Uses contextual clues for better accuracy")
        
    except AssertionError as e:
        print(f"❌ Test failed: {e}")
    except Exception as e:
        print(f"❌ Error running tests: {e}")
