#!/usr/bin/env python3
"""
Debug the specific issue with hello.tex where body text is being wrapped in math mode.
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pdf2latex.math_processor import MathProcessor
from pdf2latex.latex_generator import LaTeXGenerator


def debug_hello_world_issue():
    """Debug the specific hello world conversion issue."""
    
    print("🔍 Debugging Hello World Math Detection Issue")
    print("=" * 60)
    
    # Create the problematic text from hello.tex
    problematic_text = "Hello World Anant Kumar October 13, 2025 Hello world! This is a test document to invert using pdf2latex. 1"
    
    processor = MathProcessor()
    generator = LaTeXGenerator(template='article')
    
    print(f"Problematic text: '{problematic_text}'")
    print()
    
    # Test math detection
    is_math = processor.is_likely_math_line(problematic_text)
    print(f"Is detected as math: {is_math}")
    
    if is_math:
        print("❌ This should NOT be detected as math!")
    else:
        print("✅ Correctly identified as regular text")
    
    # Test text formatting
    formatted = generator._format_text(problematic_text)
    print(f"Formatted text: '{formatted}'")
    
    if formatted.startswith('$') and formatted.endswith('$'):
        print("❌ Text is incorrectly wrapped in math mode!")
    else:
        print("✅ Text is correctly formatted as regular text")
    
    print()
    print("Analyzing why this might be detected as math:")
    
    # Check individual components
    weak_indicators = ['x', 'y', 'z', 'α', 'β', 'γ', 'δ', 'θ', 'λ', 'μ', 'π', 'σ', 'φ', 'ψ', 'ω', 
                      '²', '³', '⁴', '₁', '₂', '₃', '∑', '∫', '∞', '≤', '≥', '≠', '±', '×', '÷',
                      '√', '∈', '∉', '⊆', '⊇', '∪', '∩', '→', '←', '↔', '∀', '∃']
    
    strong_indicators = ['=', '+', '-', '*', '/', '^', '_', '(', ')', '[', ']', '{', '}',
                        '\\', '$', '∂', '∇', '∆', 'sin', 'cos', 'tan', 'log', 'ln', 'exp',
                        'lim', 'max', 'min', 'sup', 'inf']
    
    found_weak = [indicator for indicator in weak_indicators if indicator in problematic_text]
    found_strong = [indicator for indicator in strong_indicators if indicator in problematic_text]
    
    print(f"Found weak indicators: {found_weak}")
    print(f"Found strong indicators: {found_strong}")
    
    # Test with similar but cleaner text
    print("\n" + "=" * 60)
    print("Testing with cleaner similar text:")
    
    clean_texts = [
        "Hello World",
        "This is a test document",
        "Hello world! This is a test document to convert using pdf2latex.",
        "Anant Kumar October 13, 2025",
        "Hello World Anant Kumar October 13, 2025"
    ]
    
    for text in clean_texts:
        is_math_clean = processor.is_likely_math_line(text)
        formatted_clean = generator._format_text(text)
        wrapped = formatted_clean.startswith('$') and formatted_clean.endswith('$')
        print(f"'{text[:30]}...' -> Math: {is_math_clean}, Wrapped: {wrapped}")


def create_correct_hello_world():
    """Create what the hello.tex should look like."""
    
    print("\n" + "=" * 60)
    print("Creating correct hello.tex conversion:")
    
    # Simulate the correct document structure
    correct_document = {
        'metadata': {
            'title': 'Hello World',
            'author': 'Anant Kumar',
        },
        'page_count': 1,
        'pages': [{
            'page_number': 1,
            'text': '''Hello World

Anant Kumar
October 13, 2025

Hello world! This is a test document to convert using pdf2latex.''',
        }]
    }
    
    generator = LaTeXGenerator(template='article')
    latex_output = generator.generate(correct_document)
    
    print("Correct LaTeX output should be:")
    print("-" * 40)
    print(latex_output)
    
    # Save corrected version
    output_path = Path(__file__).parent / "examples" / "hello_corrected.tex"
    output_path.write_text(latex_output, encoding='utf-8')
    print(f"\nCorrected version saved to: {output_path}")


if __name__ == '__main__':
    debug_hello_world_issue()
    create_correct_hello_world()
