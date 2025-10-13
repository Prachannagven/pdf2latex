#!/usr/bin/env python3
"""
Test script to debug mathematical expression detection issues.
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pdf2latex.math_processor import MathProcessor

def test_math_detection():
    """Test mathematical expression detection on various text samples."""
    
    processor = MathProcessor()
    
    # Test cases that should NOT be detected as math
    false_positive_cases = [
        "This is a regular sentence with normal text.",
        "The company reported a 20% increase in revenue.",
        "Please see section 3.4 for more details.",
        "The temperature was 25°C yesterday.",
        "Call me at 555-1234 for more information.",
        "The meeting is scheduled for 2:30 PM.",
        "Version 2.1 includes several bug fixes.",
        "Chapter 1: Introduction to the Subject",
        "The project deadline is December 15, 2024.",
        "Send an email to support@company.com",
        "The file size is 1.5 MB.",
        "Price: $19.99 plus tax",
        "Room 101A is available for booking.",
        "The survey had a response rate of 85%.",
        "Please refer to Figure 3.2 in the appendix."
    ]
    
    # Test cases that SHOULD be detected as math
    true_positive_cases = [
        "E = mc²",
        "a² + b² = c²",
        "f(x) = x² + 2x + 1",
        "∫ sin(x) dx = -cos(x) + C",
        "α + β = γ",
        "x^2 + y^2 = r^2",
        "log(10) = 1",
        "√(25) = 5",
        "π ≈ 3.14159",
        "∑(i=1 to n) i = n(n+1)/2"
    ]
    
    print("🔍 Testing Mathematical Expression Detection")
    print("=" * 60)
    
    print("\n❌ Cases that should NOT be detected as math:")
    print("-" * 50)
    for i, text in enumerate(false_positive_cases, 1):
        is_math = processor.is_likely_math_line(text)
        status = "❌ FALSE POSITIVE" if is_math else "✅ Correctly identified as text"
        print(f"{i:2d}. {text[:50]:<50} | {status}")
        
        if is_math:
            # Show what patterns matched
            expressions = processor.detect_math_expressions(text)
            for expr in expressions:
                print(f"    Matched: '{expr['original']}' (type: {expr['type']})")
    
    print("\n✅ Cases that SHOULD be detected as math:")
    print("-" * 50)
    for i, text in enumerate(true_positive_cases, 1):
        is_math = processor.is_likely_math_line(text)
        status = "✅ Correctly identified as math" if is_math else "❌ FALSE NEGATIVE"
        print(f"{i:2d}. {text[:50]:<50} | {status}")
    
    print("\n" + "=" * 60)
    print("Analysis complete!")

if __name__ == '__main__':
    test_math_detection()
