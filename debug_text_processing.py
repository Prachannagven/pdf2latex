#!/usr/bin/env python3
"""
Test the full text processing pipeline to identify where normal text is being treated as math.
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pdf2latex.latex_generator import LaTeXGenerator

def test_text_processing():
    """Test the full text processing pipeline."""
    
    generator = LaTeXGenerator(template='article')
    
    # Test cases with various text types
    test_cases = [
        "This is a normal paragraph with regular text that should not be treated as mathematical content.",
        "The company reported significant growth in Q3 2024.",
        "Please see Chapter 3.4 for detailed analysis of the results.",
        "The temperature measurement was 25°C at noon.",
        "Contact information: phone 555-1234, email support@company.com",
        "Version 2.1.3 includes bug fixes and performance improvements.",
        "The survey showed a 85% response rate among participants.",
        "Figure 3.2 shows the correlation between variables X and Y.",
        "Price range: $15.99 - $29.99 depending on configuration.",
        "Meeting scheduled for 2:30 PM in Conference Room 101A.",
        # Mixed content that might cause issues
        "The study examined relationships between variables a, b, and c in different contexts.",
        "Results showed that factor X increased by 2-fold compared to the control group.",
        "The algorithm processes data in O(n²) time complexity.",
        "Statistical significance was found (p < 0.05) for the primary outcome."
    ]
    
    print("🔍 Testing Full Text Processing Pipeline")
    print("=" * 80)
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n{i:2d}. Input: {text}")
        print("-" * 60)
        
        # Process through the _format_text method
        try:
            processed = generator._format_text(text)
            print(f"Output: {processed}")
            
            # Check if it got wrapped in math environment (but ignore escaped $ signs)
            is_wrapped = ('\\[' in processed and '\\]' in processed) or (processed.startswith('$') and processed.endswith('$') and not processed.startswith('\\$'))
            if is_wrapped:
                print("⚠️  WARNING: Text was wrapped in math environment!")
                
                # Let's trace what happened
                is_math_line = generator.math_processor.is_likely_math_line(text)
                expressions = generator.math_processor.detect_math_expressions(text)
                
                print(f"    is_likely_math_line: {is_math_line}")
                if expressions:
                    print(f"    Detected expressions: {expressions}")
            else:
                print("✅ Text processed as regular content")
                
        except Exception as e:
            print(f"❌ Error processing text: {e}")

def test_inline_math_detection():
    """Test the specific inline math detection logic."""
    
    generator = LaTeXGenerator(template='article')
    
    print("\n" + "=" * 80)
    print("🔍 Testing Inline Math Detection Logic")
    print("=" * 80)
    
    test_texts = [
        "Variables a, b, and c were analyzed.",
        "The coefficient β was significant.",
        "Temperature rose by 2° overnight.",
        "Results with α = 0.05 threshold.",
        "Performance improved by factor of 2x."
    ]
    
    for text in test_texts:
        print(f"\nText: {text}")
        
        # Check the actual math detection logic now used
        is_math_line = generator.math_processor.is_likely_math_line(text)
        
        print(f"  is_likely_math_line: {is_math_line}")
        
        if is_math_line:
            print(f"  → Would be processed as math!")
            expressions = generator.math_processor.detect_math_expressions(text)
            if expressions:
                print(f"  → Detected expressions: {[expr['original'] for expr in expressions]}")
        else:
            print(f"  → Processed as regular text")

if __name__ == '__main__':
    test_text_processing()
    test_inline_math_detection()
