#!/usr/bin/env python3
"""
Generate hello.tex from the actual hello.pdf with correct date format.
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pdf2latex.pdf_parser import PDFParser
from pdf2latex.latex_generator import LaTeXGenerator


def generate_hello_tex_from_pdf():
    """Generate hello.tex from the actual hello.pdf."""
    
    print("🔄 Converting hello.pdf to hello.tex with Correct Date")
    print("=" * 60)
    
    pdf_path = Path(__file__).parent / "examples" / "hello.pdf"
    tex_path = Path(__file__).parent / "examples" / "hello.tex"
    
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
        print(f"\n✅ hello.tex generated: {tex_path}")
        
        # Verify the date format
        date_lines = [line for line in latex_output.split('\n') if '\\date{' in line]
        if date_lines:
            date_line = date_lines[0]
            print(f"📅 Date command: {date_line}")
            
            if 'October 13, 2025' in date_line:
                print("✅ Date format is correct (October 13, 2025)")
                return True
            else:
                print(f"❌ Date format is unexpected: {date_line}")
                return False
        else:
            print("❌ No date command found")
            return False
            
    except Exception as e:
        print(f"❌ Error converting PDF: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = generate_hello_tex_from_pdf()
    if success:
        print("\n🎉 hello.tex successfully generated from hello.pdf with correct date format!")
    else:
        print("\n⚠️ Issues found in PDF to LaTeX conversion")
