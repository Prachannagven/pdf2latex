#!/usr/bin/env python3
"""
Step-by-step demonstration of the PDF to LaTeX conversion process.
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pdf2latex.pdf_parser import PDFParser
from pdf2latex.latex_generator import LaTeXGenerator
from rich.console import Console
from rich.panel import Panel
from rich.tree import Tree
from rich.syntax import Syntax
import json

console = Console()


def demonstrate_conversion_process():
    """Show each step of the conversion process in detail."""
    
    console.print(Panel("🔍 PDF to LaTeX Conversion Process Demonstration", style="bold magenta"))
    
    # Step 1: Show what PDF parsing extracts
    console.print("\n[bold yellow]Step 1: PDF Parsing[/bold yellow]")
    console.print("The PDF parser extracts structured data from PDF files...")
    
    # Create sample document structure (simulating what PDF parser would extract)
    sample_document = {
        'metadata': {
            'title': 'Machine Learning Research Paper',
            'author': 'Dr. Jane Smith',
            'subject': 'Artificial Intelligence',
            'creator': 'LaTeX with hyperref package',
            'creation_date': '2024-10-01',
        },
        'page_count': 2,
        'parser_used': 'pymupdf',
        'pages': [
            {
                'page_number': 1,
                'text': """Machine Learning Research Paper

ABSTRACT

This paper presents novel approaches to machine learning algorithms. We demonstrate significant improvements in accuracy and efficiency compared to existing methods.

1. INTRODUCTION

Machine learning has become increasingly important in modern computing. The field encompasses various techniques including supervised learning, unsupervised learning, and reinforcement learning.

The main contributions of this work are:
• Novel algorithm design
• Comprehensive evaluation
• Performance improvements

2. METHODOLOGY

Our approach combines traditional methods with modern techniques. We use the following mathematical formulation:

E = 1/2 * Σ(yi - ŷi)²

Where E represents the error function, yi are true values, and ŷi are predicted values.""",
                'images': [
                    {'index': 0, 'width': 400, 'height': 300, 'bbox': [100, 200, 500, 500]}
                ],
                'bbox': [0, 0, 612, 792]
            },
            {
                'page_number': 2,
                'text': """3. RESULTS

Our experiments show significant improvements:

Table 1: Performance Comparison
Method      Accuracy    Speed
Baseline    0.85        1.2s
Our Method  0.92        0.8s

4. CONCLUSION

The proposed method demonstrates superior performance across multiple metrics. Future work will focus on extending these techniques to larger datasets.

REFERENCES

[1] Smith, J. (2023). "Advanced ML Techniques", Journal of AI
[2] Brown, A. (2022). "Modern Algorithms", Conf. Proceedings""",
                'images': [],
                'bbox': [0, 0, 612, 792]
            }
        ]
    }
    
    # Show document structure as a tree
    tree = Tree("📄 Extracted Document Structure")
    
    metadata_branch = tree.add("📋 Metadata")
    for key, value in sample_document['metadata'].items():
        metadata_branch.add(f"{key}: {value}")
    
    pages_branch = tree.add(f"📖 Pages ({sample_document['page_count']})")
    for page in sample_document['pages']:
        page_branch = pages_branch.add(f"Page {page['page_number']}")
        page_branch.add(f"Text: {len(page['text'])} characters")
        page_branch.add(f"Images: {len(page['images'])} found")
        page_branch.add(f"Dimensions: {page['bbox']}")
    
    console.print(tree)
    
    # Step 2: Show LaTeX generation process
    console.print(f"\n[bold yellow]Step 2: LaTeX Generation[/bold yellow]")
    console.print("The LaTeX generator converts structured data into LaTeX source code...")
    
    # Initialize LaTeX generator
    latex_generator = LaTeXGenerator(template='article', preserve_images=True)
    
    # Generate LaTeX
    latex_content = latex_generator.generate(sample_document)
    
    console.print(f"✅ Generated LaTeX document ({len(latex_content)} characters)")
    
    # Show the LaTeX structure
    console.print("\n[bold cyan]Generated LaTeX Structure:[/bold cyan]")
    
    # Show first part of the LaTeX
    latex_lines = latex_content.split('\n')
    
    # Preamble (first ~15 lines)
    preamble_lines = latex_lines[:15]
    console.print("\n[yellow]📄 Document Preamble:[/yellow]")
    syntax = Syntax('\n'.join(preamble_lines), "latex", theme="monokai", line_numbers=True)
    console.print(syntax)
    
    # Content preview (middle section)
    content_start = 20
    content_lines = latex_lines[content_start:content_start+15]
    console.print("\n[yellow]📝 Content Preview:[/yellow]")
    syntax = Syntax('\n'.join(content_lines), "latex", theme="monokai", line_numbers=True, line_range=(content_start+1, content_start+15))
    console.print(syntax)
    
    # Save full output
    output_path = Path(__file__).parent / "demo_conversion_output.tex"
    output_path.write_text(latex_content, encoding='utf-8')
    
    console.print(f"\n[green]🎉 Full LaTeX document saved to: {output_path}[/green]")
    
    # Step 3: Show what happens with real PDFs
    console.print(f"\n[bold yellow]Step 3: Real PDF Processing[/bold yellow]")
    console.print("When processing real PDFs, the system:")
    
    process_steps = [
        "1. 📖 Opens PDF with PyMuPDF/pdfplumber/PyPDF2",
        "2. 🔍 Extracts text, fonts, images, and structure",
        "3. 🧠 Detects headings, paragraphs, lists, tables",
        "4. 🔧 Handles special characters and formatting",
        "5. ✍️  Generates proper LaTeX commands",
        "6. 💾 Saves compilable .tex file"
    ]
    
    for step in process_steps:
        console.print(f"   {step}")
    
    console.print(f"\n[blue]🔨 To test with your own PDF:[/blue]")
    console.print("   python examples/test_real_pdf.py your_file.pdf")
    
    return output_path


if __name__ == '__main__':
    demonstrate_conversion_process()
