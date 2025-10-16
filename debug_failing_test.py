#!/usr/bin/env python3
"""
Debug the failing test to see what output we're getting
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pdf2latex.latex_generator import LaTeXGenerator


def debug_failing_test():
    """Debug what output we're getting for the failing test."""
    
    print("🔍 Debugging Failing Test Output")
    print("=" * 50)
    
    # This is the test document from the failing test
    test_document = {
        'metadata': {
            'title': 'Test Document',
            'author': None,
            'date': None
        },
        'page_count': 1,
        'pages': [
            {
                'page_number': 1,
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

See Chapter 3.4 for detailed analysis.'''
            }
        ]
    }
    
    # Generate LaTeX
    generator = LaTeXGenerator(template='article')
    latex_output = generator.generate(test_document)
    
    print("Generated LaTeX:")
    print("-" * 40)
    print(latex_output)
    print("-" * 40)
    
    # Check what we got vs what's expected
    print("\nSpecific checks:")
    print(f"Contains '85\\% response rate': {'85\\% response rate' in latex_output}")
    print(f"Contains '(p < 0.05)': {'(p < 0.05)' in latex_output}")
    print(f"Contains 'O(n\\textasciicircum': {'O(n\\textasciicircum' in latex_output}")
    print(f"Contains 'E = mc': {'E = mc' in latex_output}")
    print(f"Contains '\\textasciicircum': {'\\textasciicircum' in latex_output}")
    
    # Find what we actually have for O(n²)
    if 'O(n' in latex_output:
        start = latex_output.find('O(n')
        end = start + 20
        actual_onx = latex_output[start:end]
        print(f"Actual O(n...) pattern: '{actual_onx}'")


if __name__ == '__main__':
    debug_failing_test()
