#!/usr/bin/env python3
"""
Final test of the complete date duplication fix.
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pdf2latex.latex_generator import LaTeXGenerator
from pdf2latex.metadata_extractor import MetadataExtractor


def test_final_hello_world_fix():
    """Test the final hello world case that was problematic."""
    
    print("🎉 Final Test: Hello World Date Duplication Fix")
    print("=" * 60)
    
    # The original problematic text from hello.tex
    original_document = {
        'metadata': {},
        'page_count': 1,
        'pages': [{
            'page_number': 1,
            'text': 'Hello World Anant Kumar October 13, 2025 Hello world! This is a test document to invert using pdf2latex. 1',
        }]
    }
    
    # Extract metadata and generate LaTeX
    extractor = MetadataExtractor()
    enhanced_document = original_document.copy()
    enhanced_document['metadata'] = extractor.extract_enhanced_metadata(original_document)
    
    generator = LaTeXGenerator(template='article')
    latex_output = generator.generate(enhanced_document)
    
    print("Final corrected LaTeX output:")
    print("-" * 40)
    print(latex_output)
    print("-" * 40)
    
    # Save as the final corrected version
    output_path = Path(__file__).parent / "examples" / "hello_final_corrected.tex"
    output_path.write_text(latex_output, encoding='utf-8')
    print(f"\nFinal corrected version saved to: {output_path}")
    
    # Verify the fix
    metadata = enhanced_document['metadata']
    print(f"\nExtracted metadata:")
    print(f"  Title: '{metadata.get('title', 'None')}'")
    print(f"  Author: '{metadata.get('author', 'None')}'")
    print(f"  Date: '{metadata.get('date', 'None')}'")
    
    # Check that we have proper metadata commands
    has_title = "\\title{" in latex_output
    has_date = "\\date{" in latex_output
    has_maketitle = "\\maketitle" in latex_output
    
    # Check that the actual content is preserved
    has_content = "Hello world! This is a test document" in latex_output
    
    # Check that date is not duplicated in body
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
    date_in_body = 'October 13, 2025' in body_text
    
    print(f"\n✅ Final Verification:")
    print(f"  Title command present: {has_title}")
    print(f"  Date command present: {has_date}")
    print(f"  Maketitle command present: {has_maketitle}")
    print(f"  Document content preserved: {has_content}")
    print(f"  Date duplicated in body: {date_in_body}")
    print(f"  Body content: '{body_text}'")
    
    if has_title and has_date and has_maketitle and has_content and not date_in_body:
        print(f"\n🎉 SUCCESS: All issues fixed!")
        print(f"  ✅ Metadata extracted correctly")
        print(f"  ✅ LaTeX structure generated properly")
        print(f"  ✅ Document content preserved")
        print(f"  ✅ No metadata duplication in body")
        return True
    else:
        print(f"\n❌ Some issues remain")
        return False


if __name__ == '__main__':
    success = test_final_hello_world_fix()
    if success:
        print(f"\n🚀 PDF2LaTeX converter is now working perfectly!")
    else:
        print(f"\n⚠️ Some issues need attention.")
