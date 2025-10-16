#!/usr/bin/env python3
"""
Generate corrected LaTeX from test_pdf/hello.pdf with equation environments
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pdf2latex.pdf_parser import PDFParser
from pdf2latex.latex_generator import LaTeXGenerator


def generate_corrected_tex():
    """Generate corrected LaTeX with equation environments."""
    
    print("🔧 Generating Corrected LaTeX with Equation Environments")
    print("=" * 65)
    
    pdf_path = Path(__file__).parent / "examples" / "test_pdf" / "hello.pdf"
    tex_path = Path(__file__).parent / "examples" / "test_pdf" / "hello.tex"
    
    if not pdf_path.exists():
        print(f"❌ PDF file does not exist: {pdf_path}")
        return False
    
    print(f"✅ PDF file found: {pdf_path}")
    
    try:
        # Parse the PDF
        parser = PDFParser()
        document = parser.parse(pdf_path)
        
        print(f"✅ PDF parsed successfully")
        print(f"   Pages: {document['page_count']}")
        print(f"   Title: '{document['metadata'].get('title', 'N/A')}'")
        print(f"   Author: '{document['metadata'].get('author', 'N/A')}'")
        print(f"   Date: '{document['metadata'].get('date', 'N/A')}'")
        
        # Generate LaTeX
        generator = LaTeXGenerator(template='article')
        latex_output = generator.generate(document)
        
        # Save to hello.tex
        tex_path.write_text(latex_output, encoding='utf-8')
        print(f"\n✅ LaTeX generated: {tex_path}")
        
        # Show the generated LaTeX
        print(f"\n📄 Generated LaTeX:")
        print("-" * 50)
        print(latex_output)
        print("-" * 50)
        
        # Verify equation environment
        has_equation = '\\begin{equation}' in latex_output
        has_label = '\\label{eq:' in latex_output
        has_end = '\\end{equation}' in latex_output
        
        print(f"\n📊 Equation Environment Check:")
        print(f"   Contains \\begin{{equation}}: {has_equation}")
        print(f"   Contains equation label: {has_label}")
        print(f"   Contains \\end{{equation}}: {has_end}")
        
        success = has_equation and has_label and has_end
        return success
        
    except Exception as e:
        print(f"❌ Error converting PDF: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = generate_corrected_tex()
    if success:
        print("\n🎉 LaTeX successfully generated with proper equation environments!")
    else:
        print("\n⚠️ Issues found in LaTeX generation")
