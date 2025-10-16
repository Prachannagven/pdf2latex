#!/usr/bin/env python3
"""
Debug the persistent date duplication issue.
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pdf2latex.latex_generator import LaTeXGenerator
from pdf2latex.metadata_extractor import MetadataExtractor


def debug_persistent_date_issue():
    """Debug the date duplication that's still happening."""
    
    print("🔍 Debugging Persistent Date Duplication")
    print("=" * 60)
    
    # Test the exact case that's still problematic
    document = {
        'metadata': {},
        'page_count': 1,
        'pages': [{
            'page_number': 1,
            'text': 'Hello World Anant Kumar October 13, 2025 Hello world! This is a test document to invert using pdf2latex. 1',
        }]
    }
    
    # Step by step debugging
    extractor = MetadataExtractor()
    enhanced_document = document.copy() 
    enhanced_document['metadata'] = extractor.extract_enhanced_metadata(document)
    
    print("Step 1: Metadata extraction")
    print(f"Original text: '{document['pages'][0]['text']}'")
    print("Extracted metadata:")
    for key, value in enhanced_document['metadata'].items():
        if key in ['title', 'author', 'date']:
            print(f"  {key}: '{value}'")
    
    # Test the filtering function directly
    generator = LaTeXGenerator(template='article')
    original_text = document['pages'][0]['text']
    metadata = enhanced_document['metadata']
    
    print(f"\nStep 2: Testing metadata filtering")
    print(f"Before filtering: '{original_text}'")
    
    filtered_text = generator._remove_metadata_from_text(original_text, metadata)
    print(f"After filtering: '{filtered_text}'")
    
    # Check if date is still present
    date_value = metadata.get('date', '')
    if date_value:
        date_still_present = date_value in filtered_text
        print(f"Date '{date_value}' still in filtered text: {date_still_present}")
        
        # Check for date components
        if 'October' in filtered_text:
            print("❌ 'October' still present in filtered text")
        if '2025' in filtered_text:
            print("❌ '2025' still present in filtered text")
        if '13' in filtered_text:
            print("❌ '13' still present in filtered text")
    
    # Generate full LaTeX and check final output
    print(f"\nStep 3: Full LaTeX generation")
    latex_output = generator.generate(enhanced_document)
    
    print("Generated LaTeX:")
    print("-" * 40)
    print(latex_output)
    print("-" * 40)
    
    # Check body for date duplication
    lines = latex_output.split('\n')
    body_lines = []
    after_maketitle = False
    
    for line in lines:
        if '\\maketitle' in line:
            after_maketitle = True
            continue
        if after_maketitle and not line.strip().startswith('\\end{document'):
            body_lines.append(line)
    
    body_text = '\n'.join(body_lines)
    print(f"Body text: '{body_text}'")
    
    # Check for any date components in body
    date_components = ['October', '13', '2025', 'October 13', 'October 13, 2025']
    found_in_body = []
    
    for component in date_components:
        if component in body_text:
            found_in_body.append(component)
    
    if found_in_body:
        print(f"❌ Date components found in body: {found_in_body}")
        return False
    else:
        print(f"✅ No date components found in body")
        return True


if __name__ == '__main__':
    success = debug_persistent_date_issue()
    if not success:
        print("\n🚨 Date duplication issue still exists!")
    else:
        print("\n✅ No date duplication detected")
