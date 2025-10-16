#!/usr/bin/env python3
"""
Test Unicode character normalization fix.
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pdf2latex.latex_generator import LaTeXGenerator


def test_unicode_normalization():
    """Test that Unicode minus signs are converted to ASCII hyphens."""
    
    print("🧪 Testing Unicode Character Normalization")
    print("=" * 50)
    
    generator = LaTeXGenerator()
    
    # Test cases with Unicode minus signs
    test_cases = [
        "V_{GS} −V_{th}",  # Unicode minus (U+2212)
        "a − b = c",       # Unicode minus in simple equation
        "VGS −Vth",        # No subscripts, Unicode minus
        "Mixed: V_{GS} −V_{th} and regular - dash",  # Mixed Unicode and ASCII
    ]
    
    print("Input → Output:")
    print("-" * 30)
    
    for test_case in test_cases:
        normalized = generator._normalize_unicode_characters(test_case)
        
        # Check if Unicode minus was replaced
        has_unicode_minus = '−' in test_case
        has_ascii_minus = '-' in normalized
        was_replaced = has_unicode_minus and '−' not in normalized
        
        print(f"'{test_case}'")
        print(f"  → '{normalized}'")
        print(f"  ✅ Unicode minus replaced: {was_replaced}")
        print()
    
    print("🎉 Unicode normalization test completed!")
    
    # Verify the character codes
    print("\n📊 Character Analysis:")
    unicode_minus = '−'  # U+2212
    ascii_minus = '-'    # U+002D
    
    print(f"Unicode minus '−': U+{ord(unicode_minus):04X}")
    print(f"ASCII minus   '-': U+{ord(ascii_minus):04X}")
    
    return True


if __name__ == '__main__':
    test_unicode_normalization()
