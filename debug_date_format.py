#!/usr/bin/env python3
"""
Debug the date formatting issue.
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pdf2latex.latex_generator import LaTeXGenerator
from pdf2latex.metadata_extractor import MetadataExtractor


def debug_date_formatting():
    """Debug what's happening with date formatting."""
    
    print("🔍 Debugging Date Formatting Issue")
    print("=" * 50)
    
    # Test the problematic case
    document = {
        'metadata': {},
        'page_count': 1,
        'pages': [{
            'page_number': 1,
            'text': 'Hello World Anant Kumar October 13, 2025 Hello world! This is a test document to invert using pdf2latex. 1',
        }]
    }
    
    # Extract metadata
    extractor = MetadataExtractor()
    enhanced_document = document.copy()
    enhanced_document['metadata'] = extractor.extract_enhanced_metadata(document)
    
    extracted_date = enhanced_document['metadata'].get('date', '')
    print(f"Extracted date from PDF content: '{extracted_date}'")
    
    # Test the _format_date function directly
    generator = LaTeXGenerator(template='article')
    formatted_date = generator._format_date(extracted_date)
    print(f"Formatted date by _format_date(): '{formatted_date}'")
    
    # Test the regex patterns manually
    import re
    print(f"\nTesting regex patterns against '{extracted_date}':")
    
    # PDF date pattern
    pdf_match = re.match(r'D:(\d{4})(\d{2})(\d{2})', extracted_date)
    print(f"PDF date pattern: {bool(pdf_match)}")
    
    # ISO format pattern  
    iso_match = re.match(r'(\d{4})-(\d{2})-(\d{2})', extracted_date)
    print(f"ISO format pattern: {bool(iso_match)}")
    
    # US format pattern
    us_match = re.match(r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})', extracted_date)
    print(f"US format pattern: {bool(us_match)}")
    
    # Full date string pattern (should match "October 13, 2025")
    full_date_match = re.match(r'[A-Za-z]+ \d{1,2},? \d{4}', extracted_date)
    print(f"Full date string pattern: {bool(full_date_match)}")
    
    # Generate full LaTeX and check
    latex_output = generator.generate(enhanced_document)
    
    print(f"\nGenerated LaTeX:")
    print(latex_output)
    
    # Check what appears in \date{}
    date_line = [line for line in latex_output.split('\n') if '\\date{' in line]
    if date_line:
        print(f"\nDate command in LaTeX: {date_line[0]}")
        
        if 'October 13, 2025' in date_line[0]:
            print("✅ Date preserved correctly")
            return True
        else:
            print("❌ Date was reformatted incorrectly")
            return False
    else:
        print("❌ No date command found")
        return False


if __name__ == '__main__':
    success = debug_date_formatting()
    if not success:
        print("\n⚠️ Date formatting needs to be fixed")
