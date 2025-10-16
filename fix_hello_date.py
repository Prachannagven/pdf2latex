#!/usr/bin/env python3
"""
Regenerate hello.tex with the correct date format.
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pdf2latex.latex_generator import LaTeXGenerator
from pdf2latex.metadata_extractor import MetadataExtractor


def regenerate_hello_with_correct_date():
    """Regenerate hello.tex with the correct date format."""
    
    print("🔧 Regenerating hello.tex with Correct Date Format")
    print("=" * 60)
    
    # The original input that should create the hello.tex file
    document = {
        'metadata': {},
        'page_count': 1,
        'pages': [{
            'page_number': 1,
            'text': 'Hello World Anant Kumar October 13, 2025 Hello world! This is a test document to invert using pdf2latex. 1',
        }]
    }
    
    print(f"Input text: '{document['pages'][0]['text']}'")
    
    # Extract metadata
    extractor = MetadataExtractor()
    enhanced_document = document.copy()
    enhanced_document['metadata'] = extractor.extract_enhanced_metadata(document)
    
    print(f"\nExtracted metadata:")
    for key, value in enhanced_document['metadata'].items():
        if key in ['title', 'author', 'date']:
            print(f"  {key}: '{value}'")
    
    # Generate LaTeX
    generator = LaTeXGenerator(template='article')
    latex_output = generator.generate(enhanced_document)
    
    print(f"\nGenerated LaTeX:")
    print("-" * 40)
    print(latex_output)
    print("-" * 40)
    
    # Save to hello.tex
    hello_path = Path(__file__).parent / "examples" / "hello.tex"
    hello_path.write_text(latex_output, encoding='utf-8')
    print(f"\n✅ hello.tex regenerated: {hello_path}")
    
    # Verify the date format
    date_lines = [line for line in latex_output.split('\n') if '\\date{' in line]
    if date_lines:
        date_line = date_lines[0]
        print(f"Date command: {date_line}")
        
        if 'October 13, 2025' in date_line:
            print("✅ Date format is correct (October 13, 2025)")
            return True
        elif '13/10/2025' in date_line:
            print("❌ Date format is wrong (13/10/2025)")
            return False
        else:
            print(f"❓ Unexpected date format: {date_line}")
            return False
    else:
        print("❌ No date command found")
        return False


if __name__ == '__main__':
    success = regenerate_hello_with_correct_date()
    if success:
        print("\n🎉 hello.tex successfully regenerated with correct date format!")
    else:
        print("\n⚠️ Date format issue persists")
