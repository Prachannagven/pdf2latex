#!/usr/bin/env python3
"""
Generate a corrected hello.tex file to replace the problematic one.
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pdf2latex.latex_generator import LaTeXGenerator
from pdf2latex.metadata_extractor import MetadataExtractor


def regenerate_hello_tex():
    """Regenerate the hello.tex file with our fixes."""
    
    print("🔧 Regenerating hello.tex with Latest Fixes")
    print("=" * 60)
    
    # Simulate the document that would create hello.tex
    document = {
        'metadata': {},
        'page_count': 1,
        'pages': [{
            'page_number': 1,
            'text': 'Hello World Anant Kumar October 13, 2025 Hello world! This is a test document to invert using pdf2latex. 1',
        }]
    }
    
    # Apply our latest fixes
    extractor = MetadataExtractor()
    enhanced_document = document.copy()
    enhanced_document['metadata'] = extractor.extract_enhanced_metadata(document)
    
    generator = LaTeXGenerator(template='article')
    latex_output = generator.generate(enhanced_document)
    
    print("Generated corrected LaTeX:")
    print("-" * 40)
    print(latex_output)
    print("-" * 40)
    
    # Save as the corrected hello.tex (overwriting the old one)
    hello_path = Path(__file__).parent / "examples" / "hello.tex"
    hello_path.write_text(latex_output, encoding='utf-8')
    print(f"\n✅ Corrected hello.tex saved to: {hello_path}")
    
    # Verify no date duplication
    lines = latex_output.split('\n')
    body_lines = []
    after_maketitle = False
    
    for line in lines:
        if '\\maketitle' in line:
            after_maketitle = True
            continue
        if after_maketitle and not line.strip().startswith('\\end{document'):
            body_lines.append(line)
    
    body_text = '\n'.join(body_lines).strip()
    
    # Check for date components
    date_components = ['October', '13', '2025', 'October 13', 'October 13, 2025']
    found_components = [comp for comp in date_components if comp in body_text]
    
    print(f"\nVerification:")
    print(f"Body content: '{body_text}'")
    print(f"Date components in body: {found_components}")
    
    if found_components:
        print("❌ Date duplication still exists!")
        return False
    else:
        print("✅ No date duplication - fix successful!")
        return True


if __name__ == '__main__':
    success = regenerate_hello_tex()
    if success:
        print("\n🎉 hello.tex has been corrected!")
    else:
        print("\n⚠️ Issue still exists in the generated file")
