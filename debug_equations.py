#!/usr/bin/env python3
"""
Debug equation detection in test_pdf/hello.pdf
"""

import sys
from pathlib import Path
import fitz  # PyMuPDF

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pdf2latex.pdf_parser import PDFParser
from pdf2latex.math_processor import MathProcessor
from pdf2latex.latex_generator import LaTeXGenerator


def debug_equation_detection():
    """Debug equation detection in the test PDF."""
    
    print("🔍 Debugging Equation Detection in test_pdf/hello.pdf")
    print("=" * 70)
    
    pdf_path = Path(__file__).parent / "examples" / "test_pdf" / "hello.pdf"
    
    if not pdf_path.exists():
        print(f"❌ PDF file does not exist: {pdf_path}")
        return False
    
    print(f"✅ PDF file found: {pdf_path}")
    
    # First, let's see what PyMuPDF extracts directly
    print("\n📄 Raw PDF Content (PyMuPDF):")
    print("-" * 50)
    try:
        doc = fitz.open(str(pdf_path))
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            print(f"Page {page_num + 1}:")
            print(f"Raw text: {repr(text)}")
            print(f"Readable text:")
            print(text)
            print("-" * 30)
        doc.close()
    except Exception as e:
        print(f"❌ Error reading PDF directly: {e}")
        return False
    
    # Now process with our system
    print("\n🔧 PDF2LaTeX Processing:")
    print("-" * 50)
    
    try:
        # Parse the PDF
        parser = PDFParser()
        document = parser.parse(pdf_path)
        
        print(f"✅ PDF parsed successfully")
        print(f"   Pages: {document['page_count']}")
        
        # Show extracted text per page
        for i, page in enumerate(document['pages']):
            print(f"\nPage {i + 1} extracted text:")
            print(f"Raw: {repr(page['text'])}")
            print(f"Readable:")
            print(page['text'])
        
        # Test math processor directly
        print("\n🔢 Math Processing Analysis:")
        print("-" * 50)
        
        math_processor = MathProcessor()
        
        for i, page in enumerate(document['pages']):
            page_text = page['text']
            lines = page_text.split('\n')
            
            print(f"\nPage {i + 1} - Line by line math analysis:")
            for j, line in enumerate(lines, 1):
                if not line.strip():
                    continue
                
                is_math = math_processor.is_likely_math_line(line.strip())
                print(f"  Line {j}: '{line.strip()}'")
                print(f"    → Math detected: {is_math}")
                
                # Check for equation environment markers
                if 'equation' in line.lower():
                    print(f"    → Contains 'equation': True")
                if '\\begin{' in line or '\\end{' in line:
                    print(f"    → Contains LaTeX environment: True")
        
        # Generate LaTeX and see final output
        print("\n📝 Generated LaTeX:")
        print("-" * 50)
        
        generator = LaTeXGenerator(template='article')
        latex_output = generator.generate(document)
        
        print(latex_output)
        
        # Check if equations are properly detected
        has_equation_env = '\\begin{equation}' in latex_output or '\\[' in latex_output
        print(f"\n📊 Equation Detection Summary:")
        print(f"   Contains equation environments: {has_equation_env}")
        
        return has_equation_env
        
    except Exception as e:
        print(f"❌ Error processing PDF: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = debug_equation_detection()
    if success:
        print("\n🎉 Equations detected successfully!")
    else:
        print("\n⚠️ Equation detection issues found")
