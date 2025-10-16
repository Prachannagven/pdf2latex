#!/usr/bin/env python3
"""
Test the specific fix for word boundary issues in math function detection.
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pdf2latex.math_processor import MathProcessor


def test_word_boundary_fix():
    """Test that mathematical function names don't match within other words."""
    
    processor = MathProcessor()
    
    # Test cases that should NOT be detected as math (false positives)
    false_positive_tests = [
        ("using pdf2latex converter", "sin within 'using'"),
        ("business logic implementation", "sin within 'business'"),  
        ("processing exponential data", "exp within 'exponential'"),
        ("costuming and design", "cos within 'costuming'"),
        ("tangent to the discussion", "tan within 'tangent'"),
        ("blogging about technology", "log within 'blogging'"),
        ("lunch time meeting", "ln within 'lunch'"),
        ("Hello world! This is a test document to invert using pdf2latex. 1", "original problematic text"),
    ]
    
    # Test cases that SHOULD be detected as math (true positives)
    true_positive_tests = [
        ("sin(x) = 0.5", "actual sin function"),
        ("cos(θ) + sin(θ) = 1", "actual cos and sin functions"),
        ("tan(45°) = 1", "actual tan function"), 
        ("log(x) + ln(y)", "actual log and ln functions"),
        ("exp(x) = e^x", "actual exp function"),
        ("Calculate sin( π/2 )", "sin with space before parenthesis"),
    ]
    
    print("🧪 Testing Word Boundary Fix for Math Function Detection")
    print("=" * 70)
    
    print("\n❌ These should NOT be detected as math (false positives):")
    all_false_passed = True
    for text, reason in false_positive_tests:
        is_math = processor.is_likely_math_line(text)
        status = "✅ PASS" if not is_math else "❌ FAIL"
        if is_math:
            all_false_passed = False
        print(f"{status} '{text[:50]}...' ({reason})")
    
    print("\n✅ These SHOULD be detected as math (true positives):")
    all_true_passed = True
    for text, reason in true_positive_tests:
        is_math = processor.is_likely_math_line(text)
        status = "✅ PASS" if is_math else "❌ FAIL"
        if not is_math:
            all_true_passed = False
        print(f"{status} '{text[:50]}...' ({reason})")
    
    print("\n" + "=" * 70)
    if all_false_passed and all_true_passed:
        print("🎉 All tests passed! Word boundary fix is working correctly.")
    else:
        print("⚠️  Some tests failed. The fix may need additional work.")
        if not all_false_passed:
            print("   - False positive prevention needs improvement")
        if not all_true_passed:
            print("   - True positive detection may be too restrictive")
    
    return all_false_passed and all_true_passed


if __name__ == '__main__':
    test_word_boundary_fix()
