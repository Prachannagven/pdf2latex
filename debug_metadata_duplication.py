#!/usr/bin/env python3
"""
Debug the metadata duplication issue in LaTeX generation.
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pdf2latex.latex_generator import LaTeXGenerator
from pdf2latex.metadata_extractor import MetadataExtractor


def test_metadata_duplication_issue():
    """Test the specific metadata duplication issue."""
    
    print("🔍 Testing Metadata Duplication Issue")
    print("=" * 60)
    
    # Create the problematic document structure (simulating what would come from PDF parsing)
    problematic_document = {
        'metadata': {},  # Empty initially - will be enhanced
        'page_count': 1,
        'pages': [{
            'page_number': 1,
            'text': '''Hello World

Anant Kumar
October 13, 2025

Hello world! This is a test document to convert using pdf2latex.''',
        }]
    }
    
    # Step 1: Extract metadata (this happens first)
    extractor = MetadataExtractor()
    enhanced_document = problematic_document.copy()
    enhanced_document['metadata'] = extractor.extract_enhanced_metadata(problematic_document)
    
    print("Enhanced metadata:")
    for key, value in enhanced_document['metadata'].items():
        print(f"  {key}: {value}")
    print()
    
    # Step 2: Generate LaTeX (this should not duplicate the metadata)
    generator = LaTeXGenerator(template='article')
    latex_output = generator.generate(enhanced_document)
    
    print("Generated LaTeX:")
    print("-" * 40)
    print(latex_output)
    print("-" * 40)
    
    # Check for the problem
    print("\nAnalyzing the issue:")
    
    # Check if title appears in both title command and body
    title = enhanced_document['metadata'].get('title', '')
    author = enhanced_document['metadata'].get('author', '')
    
    has_title_command = f"\\title{{{title}}}" in latex_output
    has_maketitle = "\\maketitle" in latex_output
    
    # Count occurrences of title/author text in body (after \maketitle)
    lines = latex_output.split('\n')
    after_maketitle = False
    body_lines = []
    
    for line in lines:
        if '\\maketitle' in line:
            after_maketitle = True
            continue
        if after_maketitle:
            body_lines.append(line)
    
    body_text = '\n'.join(body_lines)
    
    print(f"Title command present: {has_title_command}")
    print(f"Maketitle command present: {has_maketitle}")
    print(f"Title '{title}' appears in body: {title in body_text}")
    print(f"Author '{author}' appears in body: {author in body_text}")
    
    # The problem: title and author appear both in metadata AND in body
    if title in body_text or author in body_text:
        print("❌ PROBLEM: Metadata is duplicated in document body!")
        print(f"Body content after maketitle:\n{body_text}")
    else:
        print("✅ Good: No metadata duplication found")


def create_fixed_version():
    """Show what the corrected version should look like."""
    
    print("\n" + "=" * 60)
    print("Creating Fixed Version:")
    
    # This is what the output SHOULD look like
    correct_document = {
        'metadata': {
            'title': 'Hello World',
            'author': 'Anant Kumar',
            'date': 'October 13, 2025'
        },
        'page_count': 1,
        'pages': [{
            'page_number': 1,
            # This text should have the metadata portions removed
            'text': '''Hello world! This is a test document to convert using pdf2latex.''',
        }]
    }
    
    generator = LaTeXGenerator(template='article')
    fixed_output = generator.generate(correct_document)
    
    print("Fixed LaTeX output should be:")
    print("-" * 40)
    print(fixed_output)
    print("-" * 40)


if __name__ == '__main__':
    test_metadata_duplication_issue()
    create_fixed_version()
