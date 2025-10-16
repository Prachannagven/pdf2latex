#!/usr/bin/env python3
"""
Analyze why specific lines aren't detected as math
"""

import sys
from pathlib import Path
import re

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pdf2latex.math_processor import MathProcessor


def analyze_detection_failure():
    """Analyze why specific lines fail math detection."""
    
    print("🔍 Analyzing Math Detection Failure")
    print("=" * 50)
    
    # Test the problematic line
    test_line = "L (VGS −Vth)2"
    print(f"Analyzing: '{test_line}'")
    print()
    
    # Manual pattern checking
    print("Pattern Analysis:")
    print("-" * 30)
    
    # Check strong indicators
    strong_patterns = [
        (r'[∑∏∫∂∇∆]', 'Strong mathematical symbols'),
        (r'√\([^)]+\)', 'Square root with parentheses'),
        (r'\b(sin|cos|tan|log|ln|exp)\s*\(', 'Math functions'),
        (r'\b[a-zA-Z]\s*[=]\s*[a-zA-Z0-9\^]+\s*[+\-*/]', 'Mathematical equations'),
        (r'[a-zA-Z]\^[0-9]+\s*[+\-]', 'Algebraic expressions'),
        (r'\d+/\d+\s*[+\-*/=]', 'Fractions in math context'),
    ]
    
    for pattern, desc in strong_patterns:
        match = re.search(pattern, test_line)
        print(f"  {desc}: {bool(match)} {f'→ {match.group()}' if match else ''}")
    
    print()
    
    # Check weak indicators
    weak_patterns = [
        (r'[=<>≤≥≠≈]', 'Mathematical operators'),
        (r'[α-ωΑ-Ω]', 'Greek letters'),
        (r'[²³⁰¹⁴⁵⁶⁷⁸⁹]', 'Unicode superscripts'),
        (r'[₀₁₂₃₄₅₆₇₈₉]', 'Unicode subscripts'),
        (r'\^[0-9\-\+]', 'Explicit superscripts'),
        (r'_[0-9\-\+]', 'Explicit subscripts'),
    ]
    
    print("Weak Indicators:")
    weak_count = 0
    for pattern, desc in weak_patterns:
        match = re.search(pattern, test_line)
        if match:
            weak_count += 1
        print(f"  {desc}: {bool(match)} {f'→ {match.group()}' if match else ''}")
    
    print(f"\nWeak indicators found: {weak_count}")
    print(f"Length: {len(test_line.strip())} chars")
    
    # Check length and context rules
    text_lower = test_line.lower()
    has_common_words = any(word in text_lower for word in ['the', 'and', 'or', 'in', 'on', 'at', 'to', 'for', 'with'])
    print(f"Has common words: {has_common_words}")
    
    # Check what should trigger detection
    print(f"\nDetection rules:")
    print(f"  Strong indicators: False")
    print(f"  Weak count >= 2: {weak_count >= 2}")
    print(f"  Single weak + short + no common words: {weak_count >= 1 and len(test_line.strip()) < 30 and not has_common_words}")
    
    # The issue: "2" at the end should be detected as superscript pattern
    print(f"\nSpecific issue analysis:")
    print(f"  Text ends with digit: {test_line[-1].isdigit()}")
    print(f"  Contains parentheses with variables: {bool(re.search(r'\([A-Z]+', test_line))}")
    print(f"  Variable pattern: {bool(re.search(r'[A-Z]{2,}', test_line))}")  # VGS, Vth
    
    # Test other similar patterns
    print(f"\nTesting similar patterns:")
    similar_tests = [
        "L (VGS −Vth)²",  # With Unicode superscript
        "L (VGS-Vth)^2",  # With explicit superscript  
        "2µnCox",         # Greek letter
        "W/L",           # Fraction
    ]
    
    math_processor = MathProcessor()
    for test in similar_tests:
        is_math = math_processor.is_likely_math_line(test)
        print(f"  '{test}' → Math: {is_math}")


if __name__ == '__main__':
    analyze_detection_failure()
