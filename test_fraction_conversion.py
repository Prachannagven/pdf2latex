#!/usr/bin/env python3
"""
Debug fraction detection and conversion
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pdf2latex.math_processor import MathProcessor


def test_fraction_conversion():
    """Test fraction conversion patterns."""
    
    print("🧪 Testing Fraction Conversion")
    print("=" * 50)
    
    math_processor = MathProcessor()
    
    # Test various fraction patterns
    test_cases = [
        "1/2",  # Simple fraction
        "1 2",  # Space separated (should this become 1/2?)
        "(1/2)",  # Parenthesized fraction
        "W/L",  # Variable fraction
        "1/2µnCox",  # Mixed fraction and variables
        "ID = 1/2 µnCox W/L",  # Complete equation with fractions
        # The actual problematic case from PDF
        "ID = 1 2µnCox W L (VGS −Vth)2",
    ]
    
    print("Testing fraction patterns:")
    print("-" * 40)
    
    for test in test_cases:
        converted = math_processor.convert_to_latex(test)
        changed = converted != test
        has_frac = '\\frac{' in converted
        print(f"Input:  '{test}'")
        print(f"Output: '{converted}' {'✓' if changed else '✗'} {'[FRAC]' if has_frac else ''}")
        print()
    
    # Check the specific patterns
    print("Pattern analysis:")
    print("-" * 40)
    
    patterns = math_processor.patterns['fractions']['patterns']
    for i, pattern in enumerate(patterns):
        print(f"Fraction pattern {i+1}: {pattern}")
    
    # Test if the issue is that "1 2" should be detected as "1/2"
    print(f"\nSpecific reconstruction test:")
    print("-" * 40)
    
    # What if we try to reconstruct the fraction from the PDF structure?
    lines = ["ID = 1", "2µnCox", "W", "L (VGS −Vth)2"]
    print("Original PDF lines:")
    for i, line in enumerate(lines):
        print(f"  {i+1}: '{line}'")
    
    # The issue might be that we need pattern for "= 1" followed by "2µ" to become "= 1/2 µ"
    reconstruction_tests = [
        "= 1 2µ",  # Should become "= \frac{1}{2}\mu"
        "1 2µnCox",  # Should become "\frac{1}{2}\mu_n C_{ox}"
    ]
    
    print(f"\nReconstruction tests:")
    for test in reconstruction_tests:
        converted = math_processor.convert_to_latex(test)
        print(f"'{test}' → '{converted}'")


if __name__ == '__main__':
    test_fraction_conversion()
