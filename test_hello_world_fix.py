#!/usr/bin/env python3
"""
Test the actual hello world case that was problematic.
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pdf2latex.latex_generator import LaTeXGenerator
from pdf2latex.metadata_extractor import MetadataExtractor


def test_hello_world_fix():
    """Test the hello world case with the actual problematic text."""
    
    print("🧪 Testing Hello World Metadata Duplication Fix")
    print("=" * 60)
    
    # This is the actual problematic text from the hello.tex case
    original_document = {
        'metadata': {},
        'page_count': 1,
        'pages': [{
            'page_number': 1,
            'text': 'Hello World Anant Kumar October 13, 2025 Hello world! This is a test document to invert using pdf2latex. 1',
        }]
    }
    
    # Step 1: Extract metadata
    extractor = MetadataExtractor()
    enhanced_document = original_document.copy()
    enhanced_document['metadata'] = extractor.extract_enhanced_metadata(original_document)
    
    print("Enhanced metadata:")
    for key, value in enhanced_document['metadata'].items():
        print(f"  {key}: {value}")
    
    # Step 2: Generate LaTeX with metadata filtering
    generator = LaTeXGenerator(template='article')
    latex_output = generator.generate(enhanced_document)
    
    print(f"\nGenerated LaTeX:")
    print("-" * 40)
    print(latex_output)
    print("-" * 40)
    
    # Save the corrected version
    output_path = Path(__file__).parent / "examples" / "hello_fixed.tex"
    output_path.write_text(latex_output, encoding='utf-8')
    print(f"\nFixed version saved to: {output_path}")
    
    # Verify the fix
    has_title_cmd = "\\title{Hello World}" in latex_output
    has_author_cmd = "\\author{Anant Kumar}" in latex_output
    has_maketitle = "\\maketitle" in latex_output
    
    # Check that metadata doesn't appear in body after \maketitle
    lines = latex_output.split('\n')
    body_lines = []
    after_maketitle = False
    
    for line in lines:
        if '\\maketitle' in line:
            after_maketitle = True
            continue
        if after_maketitle:
            body_lines.append(line)
    
    body_text = '\n'.join(body_lines)
    
    title_in_body = "Hello World" in body_text
    author_in_body = "Anant Kumar" in body_text
    
    print(f"\n✅ Verification:")
    print(f"  Title command: {has_title_cmd}")
    print(f"  Author command: {has_author_cmd}")
    print(f"  Maketitle present: {has_maketitle}")
    print(f"  Title duplicated in body: {title_in_body}")
    print(f"  Author duplicated in body: {author_in_body}")
    
    if has_title_cmd and has_author_cmd and has_maketitle and not title_in_body and not author_in_body:
        print(f"\n🎉 SUCCESS: Metadata duplication fixed!")
        print(f"  • Title and author properly extracted")
        print(f"  • Maketitle command generated")
        print(f"  • No duplication in document body")
    else:
        print(f"\n❌ ISSUE: Still has problems")


if __name__ == '__main__':
    test_hello_world_fix()
