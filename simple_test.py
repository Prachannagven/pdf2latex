#!/usr/bin/env python3
"""
Simple test to regenerate hello.tex and verify no date duplication.
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pdf2latex.latex_generator import LaTeXGenerator
from pdf2latex.metadata_extractor import MetadataExtractor


def simple_regenerate_test():
    """Simple test to regenerate and verify hello.tex."""
    
    print("🔧 Simple Hello.tex Regeneration Test")
    print("=" * 50)
    
    # The exact text that should produce hello.tex
    original_text = 'Hello World Anant Kumar October 13, 2025 Hello world! This is a test document to invert using pdf2latex. 1'
    
    document = {
        'metadata': {},
        'page_count': 1,
        'pages': [{'page_number': 1, 'text': original_text}]
    }
    
    # Step 1: Extract metadata
    extractor = MetadataExtractor()
    enhanced_document = document.copy()
    enhanced_document['metadata'] = extractor.extract_enhanced_metadata(document)
    
    print(f"Metadata extracted:")
    for key, value in enhanced_document['metadata'].items():
        if key in ['title', 'author', 'date']:
            print(f"  {key}: '{value}'")
    
    # Step 2: Generate LaTeX
    generator = LaTeXGenerator(template='article')
    latex_output = generator.generate(enhanced_document)
    
    print(f"\nGenerated LaTeX:")
    print(latex_output)
    
    # Step 3: Check for date duplication in body
    lines = latex_output.split('\n')
    body_content = []
    collecting_body = False
    
    for line in lines:
        if '\\maketitle' in line:
            collecting_body = True
            continue
        elif line.strip().startswith('\\end{document}'):
            break
        elif collecting_body and line.strip():
            body_content.append(line.strip())
    
    body_text = ' '.join(body_content)
    print(f"\nBody content: '{body_text}'")
    
    # Check for date components
    date_components = ['October', '13', '2025']
    found_in_body = []
    
    for component in date_components:
        if component in body_text:
            found_in_body.append(component)
    
    if found_in_body:
        print(f"❌ Date components found in body: {found_in_body}")
        
        # Let's also test the filtering function directly
        print(f"\nDirect filtering test:")
        filtered = generator._remove_metadata_from_text(original_text, enhanced_document['metadata'])
        print(f"Filtered text: '{filtered}'")
        
        # Check if the filtering worked but LaTeX generation is the issue
        if not any(comp in filtered for comp in date_components):
            print("✅ Filtering function works correctly - issue is elsewhere")
        else:
            print("❌ Filtering function is not working")
            
        return False
    else:
        print("✅ No date duplication found!")
        
        # Save the corrected version
        hello_path = Path(__file__).parent / "examples" / "hello.tex"
        hello_path.write_text(latex_output, encoding='utf-8')
        print(f"✅ Corrected hello.tex saved")
        
        return True


if __name__ == '__main__':
    success = simple_regenerate_test()
    if success:
        print("\n🎉 hello.tex successfully corrected!")
    else:
        print("\n⚠️ Date duplication issue persists")
