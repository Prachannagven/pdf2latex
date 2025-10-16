#!/usr/bin/env python3
"""
Debug the date duplication issue specifically.
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pdf2latex.latex_generator import LaTeXGenerator
from pdf2latex.metadata_extractor import MetadataExtractor


def debug_date_duplication():
    """Debug the specific date duplication issue."""
    
    print("🔍 Debugging Date Duplication Issue")
    print("=" * 60)
    
    # Test with the problematic single-line format
    test_cases = [
        {
            'name': 'Single line format (original problem)',
            'text': 'Hello World Anant Kumar October 13, 2025 Hello world! This is a test document to invert using pdf2latex. 1'
        },
        {
            'name': 'Multi-line format',
            'text': '''Hello World

Anant Kumar
October 13, 2025

Hello world! This is a test document to convert using pdf2latex.'''
        },
        {
            'name': 'Date at end',
            'text': '''Research Paper
By John Smith
This paper discusses important topics. Published on March 15, 2024.'''
        }
    ]
    
    extractor = MetadataExtractor()
    generator = LaTeXGenerator(template='article')
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i}: {test_case['name']} ---")
        print(f"Original text: '{test_case['text'][:80]}...'")
        
        document = {
            'metadata': {},
            'page_count': 1,
            'pages': [{'page_number': 1, 'text': test_case['text']}]
        }
        
        # Extract metadata
        enhanced_document = document.copy()
        enhanced_document['metadata'] = extractor.extract_enhanced_metadata(document)
        
        print("Extracted metadata:")
        for key, value in enhanced_document['metadata'].items():
            if key in ['title', 'author', 'date']:
                print(f"  {key}: '{value}'")
        
        # Generate LaTeX
        latex_output = generator.generate(enhanced_document)
        
        # Check for date duplication
        date_value = enhanced_document['metadata'].get('date', '')
        
        # Find body content after \maketitle
        lines = latex_output.split('\n')
        body_lines = []
        after_maketitle = False
        
        for line in lines:
            if '\\maketitle' in line:
                after_maketitle = True
                continue
            if after_maketitle and not line.startswith('\\end{document'):
                body_lines.append(line)
        
        body_text = '\n'.join(body_lines).strip()
        print(f"Body content: '{body_text}'")
        
        # Check for date presence in body
        if date_value:
            # Check for various date formats that might appear
            date_components = []
            if 'October 13, 2025' in date_value:
                date_components.extend(['October 13, 2025', 'October', '2025', '13'])
            elif 'March 15, 2024' in date_value:
                date_components.extend(['March 15, 2024', 'March', '2024', '15'])
            
            date_in_body = any(comp in body_text for comp in date_components if comp)
            
            print(f"Date '{date_value}' appears in body: {date_in_body}")
            if date_in_body:
                print("❌ Date duplication detected!")
            else:
                print("✅ No date duplication")
        else:
            print("No date extracted")
        
        print(f"Full LaTeX output:\n{latex_output}")


def test_date_filtering_function():
    """Test the date filtering function directly."""
    
    print("\n" + "=" * 60)
    print("Testing Date Filtering Function Directly")
    
    generator = LaTeXGenerator(template='article')
    
    test_texts = [
        ('Hello World Anant Kumar October 13, 2025 Hello world!', 
         {'title': 'Hello World', 'author': 'Anant Kumar', 'date': 'October 13, 2025'}),
        ('Research Paper\nJohn Smith\nMarch 2024\nThis is the content.',
         {'title': 'Research Paper', 'author': 'John Smith', 'date': 'March 2024'}),
    ]
    
    for text, metadata in test_texts:
        print(f"\nOriginal: '{text}'")
        print(f"Metadata: {metadata}")
        
        filtered = generator._remove_metadata_from_text(text, metadata)
        print(f"Filtered: '{filtered}'")
        
        # Check if date components are still present
        date_value = metadata.get('date', '')
        if date_value:
            date_still_present = date_value in filtered
            print(f"Date '{date_value}' still in text: {date_still_present}")
            if date_still_present:
                print("❌ Date filtering failed!")
            else:
                print("✅ Date filtering worked")


if __name__ == '__main__':
    debug_date_duplication()
    test_date_filtering_function()
