#!/usr/bin/env python3
"""
Debug the actual hello.pdf file to see what's being extracted.
"""

import sys
from pathlib import Path
import fitz  # PyMuPDF

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pdf2latex.pdf_parser import PDFParser
from pdf2latex.metadata_extractor import MetadataExtractor
from pdf2latex.latex_generator import LaTeXGenerator


def debug_hello_pdf():
    """Debug the actual hello.pdf file."""
    
    print("🔍 Debugging hello.pdf")
    print("=" * 60)
    
    pdf_path = Path(__file__).parent / "examples" / "hello.pdf"
    
    if not pdf_path.exists():
        print(f"❌ PDF file does not exist: {pdf_path}")
        return False
    
    print(f"✅ PDF file found: {pdf_path}")
    
    # First, let's see what PyMuPDF extracts directly
    print("\n📄 Raw PDF Content (PyMuPDF):")
    print("-" * 40)
    try:
        doc = fitz.open(str(pdf_path))
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            print(f"Page {page_num + 1}:")
            print(repr(text))
            print(f"Readable text: {text}")
        doc.close()
    except Exception as e:
        print(f"❌ Error reading PDF directly: {e}")
        return False
    
    # Now use our PDF processor
    print("\n🔧 PDF2LaTeX Processing:")
    print("-" * 40)
    
    try:
        parser = PDFParser()
        document = parser.parse(pdf_path)
        
        print(f"Pages processed: {document['page_count']}")
        for i, page in enumerate(document['pages']):
            print(f"Page {i + 1} text: {repr(page['text'])}")
        
        # Extract metadata
        extractor = MetadataExtractor()
        enhanced_document = document.copy()
        enhanced_document['metadata'] = extractor.extract_enhanced_metadata(document)
        
        print(f"\nExtracted metadata:")
        for key, value in enhanced_document['metadata'].items():
            print(f"  {key}: '{value}'")
        
        # Generate LaTeX
        generator = LaTeXGenerator(template='article')
        latex_output = generator.generate(enhanced_document)
        
        print(f"\nGenerated LaTeX:")
        print("-" * 40)
        print(latex_output)
        print("-" * 40)
        
        # Check for date in the LaTeX
        date_lines = [line for line in latex_output.split('\n') if '\\date{' in line]
        if date_lines:
            date_line = date_lines[0]
            print(f"\n📅 Date command: {date_line}")
            
            if 'October 13, 2025' in date_line:
                print("✅ Date format is correct (October 13, 2025)")
                return True
            else:
                print(f"❌ Date format is not October 13, 2025")
                return False
        else:
            print("❌ No date command found")
            return False
            
    except Exception as e:
        print(f"❌ Error processing PDF: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = debug_hello_pdf()
    if success:
        print("\n🎉 PDF processed successfully with correct date!")
    else:
        print("\n⚠️ Issues found in PDF processing")
