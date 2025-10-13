#!/usr/bin/env python3
"""
Debug the integration test to see what's happening.
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pdf2latex.math_processor import MathProcessor
from pdf2latex.latex_generator import LaTeXGenerator


def debug_integration():
    """Debug the integration test."""
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
    
    print("Generated LaTeX output:")
    print("=" * 60)
    print(latex_output)
    print("=" * 60)
    
    # Check what we're looking for
    print("\nChecking for expected content:")
    print(f"Contains '85\\% response rate': {'85\\% response rate' in latex_output}")
    print(f"Contains '(p < 0.05)': {'(p < 0.05)' in latex_output}")
    print(f"Contains 'O(n\\textasciicircum': {'O(n\\textasciicircum' in latex_output}")
    print(f"Contains 'E = mc': {'E = mc' in latex_output}")
    print(f"Contains 'a^{2} + b^{2} = c^{2}': {'a^{2} + b^{2} = c^{2}' in latex_output}")
    print(f"Contains 'a² + b² = c²': {'a² + b² = c²' in latex_output}")
    
    # Test individual lines
    print("\nTesting individual lines:")
    test_lines = [
        "The survey showed a 85% response rate among participants.",
        "Statistical significance was found (p < 0.05) for the primary outcome.",
        "The algorithm processes data in O(n²) time complexity.",
        "The famous equation E = mc² relates energy and mass.",
        "For right triangles: a² + b² = c²"
    ]
    
    for line in test_lines:
        is_math = processor.is_likely_math_line(line)
        formatted = generator._format_text(line)
        print(f"'{line[:50]}...' -> Math: {is_math}, Formatted: '{formatted[:50]}...'")


if __name__ == '__main__':
    debug_integration()
