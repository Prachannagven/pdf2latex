#!/usr/bin/env python3
"""
Test specific math detection for the problematic lines
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pdf2latex.math_processor import MathProcessor


def test_specific_lines():
    """Test math detection for specific problematic lines."""
    
    print("🧪 Testing Math Detection for Specific Lines")
    print("=" * 60)
    
    math_processor = MathProcessor()
    
    test_lines = [
        "ID = 1",
        "2µnCox",
        "W",
        "L (VGS −Vth)2",
        "(1)",
        "1",
        # Combined lines to test multi-line detection
        "ID = 1 2µnCox W",
        "L (VGS −Vth)2",
        "ID = (1/2)µnCox(W/L)(VGS-Vth)²",  # How it should look
    ]
    
    print("Individual line analysis:")
    print("-" * 40)
    for line in test_lines:
        is_math = math_processor.is_likely_math_line(line)
        processed = math_processor.convert_to_latex(line)
        wrapped = math_processor.wrap_math_expressions(line)
        
        print(f"Line: '{line}'")
        print(f"  Math detected: {is_math}")
        print(f"  Processed: '{processed}'")
        print(f"  Wrapped: '{wrapped}'")
        print()
    
    # Test what the system should ideally reconstruct
    print("Ideal reconstruction:")
    print("-" * 40)
    ideal_equation = "I_D = \\frac{1}{2}\\mu_n C_{ox} \\frac{W}{L}(V_{GS} - V_{th})^2"
    print(f"Target LaTeX: {ideal_equation}")
    
    # Test if we can detect this as a complete equation block
    full_text = """ID = 1
2µnCox
W
L (VGS −Vth)2
(1)"""
    
    print(f"\nFull text block:")
    print(f"'{full_text}'")
    
    lines = full_text.split('\n')
    math_lines = [line for line in lines if math_processor.is_likely_math_line(line.strip())]
    
    print(f"Math lines detected: {len(math_lines)} out of {len(lines)}")
    for i, line in enumerate(lines):
        is_math = math_processor.is_likely_math_line(line.strip())
        print(f"  Line {i+1}: '{line.strip()}' → Math: {is_math}")


if __name__ == '__main__':
    test_specific_lines()
