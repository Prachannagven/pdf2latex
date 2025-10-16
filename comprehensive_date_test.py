#!/usr/bin/env python3
"""
Comprehensive test for date duplication across multiple scenarios.
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pdf2latex.latex_generator import LaTeXGenerator
from pdf2latex.metadata_extractor import MetadataExtractor


def test_multiple_date_scenarios():
    """Test date filtering across multiple scenarios."""
    
    print("🧪 Comprehensive Date Duplication Test")
    print("=" * 60)
    
    test_cases = [
        {
            'name': 'Single line with date (hello.tex case)',
            'text': 'Hello World Anant Kumar October 13, 2025 Hello world! This is a test document to invert using pdf2latex. 1'
        },
        {
            'name': 'Multi-line with date',
            'text': '''Hello World
Anant Kumar
October 13, 2025
Hello world! This is a test document to convert using pdf2latex.'''
        },
        {
            'name': 'Date in different format',
            'text': 'Research Paper John Smith March 15, 2024 This paper discusses important topics.'
        },
        {
            'name': 'Date with slashes',
            'text': 'Simple Title Author Name 10/14/2025 Document content here.'
        },
        {
            'name': 'Month-year format',
            'text': 'Article Title By Jane Doe March 2024 Content of the article begins here.'
        }
    ]
    
    extractor = MetadataExtractor()
    generator = LaTeXGenerator(template='article')
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test {i}: {test_case['name']} ---")
        print(f"Input: '{test_case['text'][:80]}...'")
        
        document = {
            'metadata': {},
            'page_count': 1,
            'pages': [{'page_number': 1, 'text': test_case['text']}]
        }
        
        # Extract metadata
        enhanced_document = document.copy()
        enhanced_document['metadata'] = extractor.extract_enhanced_metadata(document)
        
        # Show extracted metadata
        metadata = enhanced_document['metadata']
        extracted_date = metadata.get('date', '')
        
        print(f"Extracted date: '{extracted_date}'")
        
        # Generate LaTeX
        latex_output = generator.generate(enhanced_document)
        
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
        
        body_text = '\n'.join(body_lines).strip()
        print(f"Body content: '{body_text}'")
        
        # Check for date components in body
        date_found_in_body = False
        if extracted_date:
            # Check for exact date
            if extracted_date in body_text:
                date_found_in_body = True
                print(f"❌ Exact date '{extracted_date}' found in body")
            
            # Check for date components
            date_components = []
            if 'October' in extracted_date:
                date_components.extend(['October', '13', '2025'])
            elif 'March' in extracted_date:
                date_components.extend(['March', '15', '2024'])
            elif '10/14/2025' in extracted_date:
                date_components.extend(['10/14/2025', '10', '14', '2025'])
            
            found_components = [comp for comp in date_components if comp in body_text]
            if found_components:
                date_found_in_body = True
                print(f"❌ Date components found in body: {found_components}")
        
        if date_found_in_body:
            print(f"❌ FAIL: Date duplication detected")
            all_passed = False
        else:
            print(f"✅ PASS: No date duplication")
    
    print(f"\n" + "=" * 60)
    if all_passed:
        print("🎉 All date duplication tests PASSED!")
        print("✅ Date filtering is working correctly across all scenarios")
    else:
        print("❌ Some date duplication tests FAILED!")
        print("⚠️ Date filtering needs improvement")
    
    return all_passed


if __name__ == '__main__':
    success = test_multiple_date_scenarios()
    if success:
        print("\n✅ Date duplication issue is fully resolved!")
    else:
        print("\n⚠️ Date duplication issue still exists in some cases")
