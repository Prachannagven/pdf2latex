#!/usr/bin/env python3
"""
Test enhanced mathematical expression and image extraction features.
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pdf2latex.math_processor import MathProcessor
from pdf2latex.image_processor import ImageProcessor
from pdf2latex import PDF2LaTeXConverter
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

console = Console()


def test_math_processing():
    """Test the mathematical expression processing."""
    console.print(Panel("🧮 Testing Mathematical Expression Processing", style="bold blue"))
    
    math_processor = MathProcessor()
    
    # Test cases for mathematical expressions
    test_cases = [
        "The famous equation E = mc² demonstrates mass-energy equivalence.",
        "In geometry, the Pythagorean theorem states that a² + b² = c².",
        "The quadratic formula is x = (-b ± √(b² - 4ac)) / 2a.",
        "Greek letters are common: α, β, γ, δ, θ, π, λ, μ, σ, ω.",
        "Mathematical operators: ≤, ≥, ≠, ≈, ∞, ∑, ∏, ∫.",
        "Functions: sin(x), cos(x), tan(x), log(x), ln(x), exp(x).",
        "Fractions: 1/2, 3/4, (x+1)/(x-1).",
        "Subscripts: H₂O, CO₂, x₁, y₂.",
        "Mixed: The area formula A = πr² uses π ≈ 3.14159."
    ]
    
    table = Table(title="Mathematical Expression Conversion Results")
    table.add_column("Original", style="cyan")
    table.add_column("LaTeX", style="green")
    table.add_column("Math Detected", style="yellow")
    
    for test_case in test_cases:
        converted = math_processor.convert_to_latex(test_case)
        is_math = math_processor.is_likely_math_line(test_case)
        
        table.add_row(
            test_case[:50] + "..." if len(test_case) > 50 else test_case,
            converted[:50] + "..." if len(converted) > 50 else converted,
            "✅" if is_math else "❌"
        )
    
    console.print(table)
    
    # Test math expression detection
    console.print("\n[yellow]🔍 Mathematical Expression Detection:[/yellow]")
    sample_text = "The equation E = mc² and Pythagorean theorem a² + b² = c² are fundamental."
    expressions = math_processor.detect_math_expressions(sample_text)
    
    for expr in expressions:
        console.print(f"  • Found {expr['type']}: '{expr['original']}' at position {expr['start']}-{expr['end']}")


def test_enhanced_conversion():
    """Test the enhanced conversion with math and image processing."""
    console.print(Panel("🚀 Testing Enhanced PDF2LaTeX Conversion", style="bold magenta"))
    
    # Create sample document with mathematical content
    sample_document = {
        'metadata': {
            'title': 'Advanced Mathematics and Physics',
            'author': 'Dr. Albert Einstein',
            'subject': 'Mathematical Physics',
        },
        'page_count': 1,
        'parser_used': 'enhanced_demo',
        'pages': [
            {
                'page_number': 1,
                'text': """Advanced Mathematics and Physics

FUNDAMENTAL EQUATIONS

The most famous equation in physics is Einstein's mass-energy equivalence:

E = mc²

Where E is energy, m is mass, and c is the speed of light.

GEOMETRY AND TRIGONOMETRY

The Pythagorean theorem is fundamental in geometry:

a² + b² = c²

Trigonometric functions are essential:
• sin(θ) = opposite/hypotenuse
• cos(θ) = adjacent/hypotenuse  
• tan(θ) = opposite/adjacent

CALCULUS

Integration and differentiation:
∫ f(x) dx and ∂f/∂x

The fundamental theorem: ∫[a,b] f'(x) dx = f(b) - f(a)

GREEK LETTERS AND SYMBOLS

Common Greek letters in mathematics:
α (alpha), β (beta), γ (gamma), δ (delta)
π ≈ 3.14159, e ≈ 2.71828
Inequalities: x ≤ y, a ≥ b, p ≠ q
Special: ∞ (infinity), ∑ (sum), ∏ (product)

FRACTIONS AND SUBSCRIPTS

Chemical formulas: H₂O, CO₂, C₆H₁₂O₆
Mathematical expressions: x₁ + x₂ = x₃
Fractions: 1/2 + 3/4 = 5/4""",
                'images': [],
                'bbox': [0, 0, 612, 792]
            }
        ]
    }
    
    # Test conversion
    converter = PDF2LaTeXConverter(template='article', preserve_images=True)
    latex_content = converter.generate_latex(sample_document)
    
    # Save output
    output_path = Path(__file__).parent / "enhanced_math_output.tex"
    output_path.write_text(latex_content, encoding='utf-8')
    
    console.print(f"✅ Enhanced conversion completed!")
    console.print(f"📄 Output saved to: {output_path}")
    console.print(f"📏 Content length: {len(latex_content)} characters")
    
    # Show enhanced LaTeX preview
    console.print("\n[yellow]📄 Enhanced LaTeX Output Preview:[/yellow]")
    latex_lines = latex_content.split('\n')
    preview_lines = latex_lines[15:45]  # Show content section
    preview_content = '\n'.join(preview_lines)
    
    syntax = Syntax(preview_content, "latex", theme="monokai", line_numbers=True, line_range=(16, 45))
    console.print(syntax)
    
    return output_path


def demonstrate_features():
    """Demonstrate all enhanced features."""
    console.print(Panel("🌟 PDF2LaTeX Enhanced Features Demonstration", style="bold cyan"))
    
    # Test mathematical processing
    test_math_processing()
    
    console.print("\n" + "="*80 + "\n")
    
    # Test enhanced conversion
    output_path = test_enhanced_conversion()
    
    console.print(f"\n[green]🎉 All enhanced features demonstrated successfully![/green]")
    console.print(f"\n[blue]📚 Features implemented:[/blue]")
    console.print("  ✅ Advanced mathematical expression detection")
    console.print("  ✅ LaTeX math symbol conversion")
    console.print("  ✅ Greek letter recognition")
    console.print("  ✅ Superscript/subscript handling")
    console.print("  ✅ Mathematical operator conversion")
    console.print("  ✅ Image extraction framework (ready for real PDFs)")
    console.print("  ✅ Enhanced text formatting")
    
    console.print(f"\n[blue]🔨 To compile the enhanced LaTeX:[/blue]")
    console.print(f"  cd {output_path.parent}")
    console.print(f"  pdflatex {output_path.name}")
    
    console.print(f"\n[blue]🧪 To test with real PDFs:[/blue]")
    console.print("  python examples/test_real_pdf.py your_document.pdf")


if __name__ == '__main__':
    demonstrate_features()
