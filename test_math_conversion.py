#!/usr/bin/env python3
"""
Test mathematical content conversion to see what's missing
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pdf2latex.math_processor import MathProcessor


def test_math_conversion():
    """Test mathematical content conversion."""
    
    print("🧪 Testing Mathematical Content Conversion")
    print("=" * 60)
    
    math_processor = MathProcessor()
    
    # Test the problematic equation parts
    test_cases = [
        "ID = 1",
        "2µnCox", 
        "W",
        "L (VGS −Vth)2",
        "ID = 1 2µnCox W L (VGS −Vth)2",  # Combined equation
        # Individual components that should be converted
        "µ",        # Greek mu
        "VGS",      # Should become V_{GS}
        "Vth",      # Should become V_{th}
        "Cox",      # Should become C_{ox}
        "(VGS −Vth)2",  # Should become (V_{GS} - V_{th})^2
        "W/L",      # Should become \frac{W}{L}
        "1/2",      # Should become \frac{1}{2}
        "ID",       # Should become I_D
    ]
    
    print("Testing individual conversions:")
    print("-" * 40)
    
    for test in test_cases:
        converted = math_processor.convert_to_latex(test)
        changed = converted != test
        print(f"'{test}' → '{converted}' {'✓' if changed else '✗'}")
    
    print(f"\nTesting ideal target equation:")
    print("-" * 40)
    ideal_input = "ID = (1/2) * µnCox * (W/L) * (VGS - Vth)^2"
    ideal_converted = math_processor.convert_to_latex(ideal_input)
    print(f"Input:  '{ideal_input}'")
    print(f"Output: '{ideal_converted}'")
    
    # Check Greek letter patterns
    print(f"\nGreek letter patterns:")
    print("-" * 40)
    print("Available Greek letters:")
    for greek, latex in math_processor.greek_letters.items():
        print(f"  '{greek}' → '{latex}'")
    
    # Check defined patterns
    print(f"\nDefined conversion patterns:")
    print("-" * 40)
    for category, pattern_data in math_processor.patterns.items():
        print(f"{category}:")
        patterns = pattern_data['patterns']
        for i, pattern in enumerate(patterns):
            print(f"  Pattern {i+1}: {pattern}")


if __name__ == '__main__':
    test_math_conversion()
