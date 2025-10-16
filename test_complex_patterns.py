#!/usr/bin/env python3
"""
Test specific complex patterns
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pdf2latex.math_processor import MathProcessor


def test_complex_patterns():
    """Test complex mathematical patterns."""
    
    print("🧪 Testing Complex Mathematical Patterns")
    print("=" * 50)
    
    math_processor = MathProcessor()
    
    # Test specific problematic cases
    test_cases = [
        ("µnCox", "\\mu_n C_{ox}"),
        ("2µnCox", "2\\mu_n C_{ox}"),
        ("µnCox W/L", "\\mu_n C_{ox} \\frac{W}{L}"),
        ("ID = 1 2µnCox W L (VGS −Vth)2", "I_D = \\frac{1}{2}\\mu_n C_{ox} \\frac{W}{L}(V_{GS} - V_{th})^2"),
    ]
    
    print("Testing complex pattern conversions:")
    print("-" * 40)
    
    for input_text, expected in test_cases:
        converted = math_processor.convert_to_latex(input_text)
        success = "✓" if converted != input_text else "✗"
        print(f"Input:    '{input_text}'")
        print(f"Expected: '{expected}'")
        print(f"Got:      '{converted}' {success}")
        print()


if __name__ == '__main__':
    test_complex_patterns()
