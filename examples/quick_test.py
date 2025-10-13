#!/usr/bin/env python3
"""
Quick test - create a simple PDF and convert it to LaTeX
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pdf2latex import PDF2LaTeXConverter
from rich.console import Console

console = Console()

def quick_test():
    """Quick test of PDF to LaTeX conversion."""
    
    # Create a sample document structure (simulating PDF content)
    sample_doc = {
        'metadata': {'title': 'Quick Test Document', 'author': 'PDF2LaTeX'},
        'page_count': 1,
        'parser_used': 'demo',
        'pages': [{
            'page_number': 1,
            'text': '''Quick Test Document

MATHEMATICAL EXPRESSIONS

Einstein's famous equation: E = mc²
Pythagorean theorem: a² + b² = c²
Greek letters: α + β = γ
Functions: sin(π/2) = 1
Fractions: x = 1/2 + 3/4

RESULTS

This demonstrates the enhanced mathematical processing capabilities of PDF2LaTeX.''',
            'images': [],
            'bbox': [0, 0, 612, 792]
        }]
    }
    
    console.print("[bold blue]🚀 Quick PDF2LaTeX Test[/bold blue]")
    
    # Convert to LaTeX
    converter = PDF2LaTeXConverter(template='article', preserve_images=True)
    latex_content = converter.generate_latex(sample_doc)
    
    # Save output
    output_file = Path(__file__).parent / "quick_test_output.tex"
    output_file.write_text(latex_content, encoding='utf-8')
    
    console.print(f"✅ Test completed! Output saved to: {output_file}")
    console.print(f"📏 Generated {len(latex_content)} characters of LaTeX")
    
    # Show preview
    lines = latex_content.split('\n')[:20]
    console.print("\n[yellow]📄 LaTeX Preview:[/yellow]")
    for i, line in enumerate(lines, 1):
        console.print(f"{i:2d}: {line}")
    
    console.print(f"\n[blue]🔨 To compile:[/blue]")
    console.print(f"cd {output_file.parent}")
    console.print(f"pdflatex {output_file.name}")
    
    return output_file

if __name__ == '__main__':
    quick_test()
