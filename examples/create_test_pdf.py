#!/usr/bin/env python3
"""
Create a simple test PDF for demonstrating the conversion process.
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter


def create_test_pdf():
    """Create a simple test PDF with various content types."""
    output_path = Path(__file__).parent / "test_document.pdf"
    
    # Create PDF
    c = canvas.Canvas(str(output_path), pagesize=letter)
    width, height = letter
    
    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height - 100, "Sample Document for PDF2LaTeX Testing")
    
    # Subtitle
    c.setFont("Helvetica", 12)
    c.drawString(100, height - 130, "This document demonstrates various content types")
    
    # Section 1
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, height - 180, "1. Introduction")
    
    c.setFont("Helvetica", 11)
    text_lines = [
        "This is a sample document created to test the PDF to LaTeX converter.",
        "The document contains various types of content including headings,",
        "paragraphs, and different formatting styles."
    ]
    
    y_pos = height - 210
    for line in text_lines:
        c.drawString(120, y_pos, line)
        y_pos -= 20
    
    # Section 2
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, height - 300, "2. Features to Test")
    
    c.setFont("Helvetica", 11)
    feature_lines = [
        "• Text extraction and formatting",
        "• Heading detection and conversion",
        "• Special characters: & % $ # ^ _ { } ~ \\",
        "• Mathematical notation: E = mc² and a² + b² = c²"
    ]
    
    y_pos = height - 330
    for line in feature_lines:
        c.drawString(120, y_pos, line)
        y_pos -= 20
    
    # Section 3
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, height - 450, "3. Conclusion")
    
    c.setFont("Helvetica", 11)
    c.drawString(120, height - 480, "This test document should convert to proper LaTeX format.")
    
    # Save PDF
    c.save()
    
    print(f"Test PDF created: {output_path}")
    return output_path


if __name__ == '__main__':
    try:
        pdf_path = create_test_pdf()
        print(f"✅ Successfully created test PDF: {pdf_path}")
    except ImportError:
        print("❌ reportlab not installed. Install with: pip install reportlab")
        print("Creating a simple text-based test instead...")
        
        # Alternative: show how to test with existing PDFs
        print("\n📋 To test with your own PDF:")
        print("1. Place any PDF file in the examples/ directory")
        print("2. Run: python examples/test_real_pdf.py your_file.pdf")
