#!/usr/bin/env python3
"""
Debug why date filtering isn't working properly.
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pdf2latex.latex_generator import LaTeXGenerator
from pdf2latex.metadata_extractor import MetadataExtractor


def debug_date_filtering_step_by_step():
    """Debug the date filtering step by step."""
    
    print("🔍 Step-by-Step Date Filtering Debug")
    print("=" * 60)
    
    # The problematic text
    original_text = 'Hello World Anant Kumar October 13, 2025 Hello world! This is a test document to invert using pdf2latex. 1'
    
    # Extract metadata first
    document = {
        'metadata': {},
        'page_count': 1,
        'pages': [{'page_number': 1, 'text': original_text}]
    }
    
    extractor = MetadataExtractor()
    enhanced_document = document.copy()
    enhanced_document['metadata'] = extractor.extract_enhanced_metadata(document)
    
    metadata = enhanced_document['metadata']
    title = metadata.get('title', '').strip()
    author = metadata.get('author', '').strip()
    date = metadata.get('date', '').strip()
    
    print(f"Original text: '{original_text}'")
    print(f"Extracted title: '{title}'")
    print(f"Extracted author: '{author}'")
    print(f"Extracted date: '{date}'")
    
    # Test the filtering function step by step
    generator = LaTeXGenerator(template='article')
    
    print(f"\nTesting single-line filtering logic:")
    
    # Simulate the _filter_single_line_metadata function step by step
    result = original_text.strip()
    print(f"Step 1 - Start: '{result}'")
    
    # Remove title
    if title and result.startswith(title):
        result = result[len(title):].strip()
        print(f"Step 2 - After removing title '{title}': '{result}'")
    else:
        print(f"Step 2 - Title '{title}' not at start, skipping")
    
    # Remove author
    if author and result.startswith(author):
        result = result[len(author):].strip()
        print(f"Step 3 - After removing author '{author}': '{result}'")
    else:
        print(f"Step 3 - Author '{author}' not at start, skipping")
    
    # Remove date
    if date:
        print(f"Step 4 - Attempting to remove date '{date}'")
        if date in result:
            result = result.replace(date, '', 1).strip()
            print(f"Step 4a - After exact date removal: '{result}'")
        else:
            print(f"Step 4a - Exact date '{date}' not found in '{result}'")
            
            # Try date patterns
            import re
            date_patterns = [
                r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4}\b',
                r'\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b',
                r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',
                r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b',
            ]
            
            for i, pattern in enumerate(date_patterns):
                if re.search(pattern, result, flags=re.IGNORECASE):
                    old_result = result
                    result = re.sub(pattern, '', result, flags=re.IGNORECASE).strip()
                    print(f"Step 4b.{i+1} - Pattern '{pattern}' matched, result: '{result}'")
                    break
            else:
                print(f"Step 4b - No date patterns matched in '{result}'")
    
    # Clean up
    result = re.sub(r'\s+', ' ', result)
    result = re.sub(r'^[,\-\s]+|[,\-\s]+$', '', result)
    print(f"Step 5 - After cleanup: '{result}'")
    
    # Now test the actual function
    print(f"\nTesting actual _remove_metadata_from_text function:")
    actual_filtered = generator._remove_metadata_from_text(original_text, metadata)
    print(f"Function result: '{actual_filtered}'")
    
    # Compare
    if result == actual_filtered:
        print("✅ Manual steps match function result")
    else:
        print("❌ Manual steps don't match function result")
        print(f"Manual: '{result}'")
        print(f"Function: '{actual_filtered}'")
    
    # Test full LaTeX generation
    print(f"\nTesting full LaTeX generation:")
    latex_output = generator.generate(enhanced_document)
    
    # Extract body
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
    print(f"Final body text: '{body_text}'")
    
    # Check for date components
    date_components = ['October', '13', '2025', 'October 13', 'October 13, 2025']
    found_components = [comp for comp in date_components if comp in body_text]
    
    if found_components:
        print(f"❌ Date components still in body: {found_components}")
        return False
    else:
        print(f"✅ No date components in body")
        return True


if __name__ == '__main__':
    success = debug_date_filtering_step_by_step()
    if not success:
        print("\n🚨 Date filtering is not working correctly!")
    else:
        print("\n✅ Date filtering is working correctly")
