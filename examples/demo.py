#!/usr/bin/env python3
"""
Example script demonstrating the PDF2LaTeX converter with simulated PDF content.
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pdf2latex import PDF2LaTeXConverter


def create_sample_document():
    """Create a sample document structure that simulates PDF parser output."""
    return {
        'metadata': {
            'title': 'Sample Test Document',
            'author': 'PDF2LaTeX Converter',
            'subject': 'Testing document conversion',
        },
        'page_count': 1,
        'parser_used': 'simulated',
        'pages': [
            {
                'page_number': 1,
                'text': """Sample Test Document

INTRODUCTION

This document contains various types of content to test the conversion capabilities.

Basic Text Processing

The converter should be able to handle regular paragraphs like this one. It should preserve the basic text formatting and structure while converting it to proper LaTeX format.

Some basic mathematical expressions: E = mc^2 and the Pythagorean theorem a^2 + b^2 = c^2.

CONCLUSION

This concludes our test document. The converter should be able to extract this content and generate appropriate LaTeX code.""",
                'images': [],
                'bbox': [0, 0, 612, 792]
            }
        ]
    }


def main():
    """Main function to demonstrate the converter."""
    print("PDF2LaTeX Converter - Example Demo")
    print("=" * 40)
    
    # Initialize the converter
    converter = PDF2LaTeXConverter(template='article')
    
    # Create sample document (simulating PDF parsing)
    document = create_sample_document()
    
    print(f"Sample document created with {document['page_count']} page(s)")
    print(f"Title: {document['metadata']['title']}")
    print(f"Author: {document['metadata']['author']}")
    print()
    
    # Generate LaTeX
    print("Generating LaTeX...")
    latex_content = converter.generate_latex(document)
    
    # Save to file
    output_path = Path(__file__).parent / "sample_output.tex"
    output_path.write_text(latex_content, encoding='utf-8')
    
    print(f"LaTeX content generated and saved to: {output_path}")
    print(f"Content length: {len(latex_content)} characters")
    print()
    
    # Show first few lines of the output
    lines = latex_content.split('\n')
    print("First 20 lines of generated LaTeX:")
    print("-" * 40)
    for i, line in enumerate(lines[:20], 1):
        print(f"{i:2d}: {line}")
    
    if len(lines) > 20:
        print(f"... and {len(lines) - 20} more lines")
    
    print()
    print(f"Full LaTeX content saved to: {output_path}")
    print("You can compile this with: pdflatex sample_output.tex")


if __name__ == '__main__':
    main()
