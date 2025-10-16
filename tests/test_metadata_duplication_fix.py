#!/usr/bin/env python3
"""
Test for metadata duplication fix in LaTeX generation.
"""

import pytest
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pdf2latex.latex_generator import LaTeXGenerator
from pdf2latex.metadata_extractor import MetadataExtractor


class TestMetadataDuplicationFix:
    """Test cases for metadata duplication fix."""
    
    def setup_method(self):
        """Set up test cases."""
        self.extractor = MetadataExtractor()
        self.generator = LaTeXGenerator(template='article')
    
    def test_title_not_duplicated_in_body(self):
        """Test that title extracted for metadata is not duplicated in document body."""
        document = {
            'metadata': {},
            'page_count': 1,
            'pages': [{
                'page_number': 1,
                'text': '''Machine Learning Research

Dr. Jane Smith
March 2024

This paper presents novel approaches to machine learning algorithms.''',
            }]
        }
        
        # Extract metadata
        enhanced_document = document.copy()
        enhanced_document['metadata'] = self.extractor.extract_enhanced_metadata(document)
        
        # Generate LaTeX
        latex_output = self.generator.generate(enhanced_document)
        
        # Verify title is in metadata commands but not duplicated in body
        assert '\\title{' in latex_output, "Title command should be present"
        assert '\\maketitle' in latex_output, "Maketitle command should be present"
        
        # Check body content (after \maketitle)
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
        title = enhanced_document['metadata'].get('title', '')
        
        # Title should not appear as a heading in the body
        assert f'\\section{{{title}}}' not in body_text, f"Title should not be duplicated as section in body"
        
        # Main content should still be present
        assert 'This paper presents novel approaches' in body_text, "Main content should be preserved"
    
    def test_author_not_duplicated_in_body(self):
        """Test that author extracted for metadata is not duplicated in document body."""
        document = {
            'metadata': {},
            'page_count': 1,
            'pages': [{
                'page_number': 1,
                'text': '''Research Study

John Doe
University of Example
2024

This document explores various research methodologies.''',
            }]
        }
        
        # Extract metadata
        enhanced_document = document.copy()
        enhanced_document['metadata'] = self.extractor.extract_enhanced_metadata(document)
        
        # Generate LaTeX
        latex_output = self.generator.generate(enhanced_document)
        
        # Check body content
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
        author = enhanced_document['metadata'].get('author', '')
        
        # Author should not appear as a section in the body if it was extracted as metadata
        if author:
            assert f'\\section{{{author}}}' not in body_text, f"Author should not be duplicated as section in body"
        
        # Main content should still be present
        assert 'This document explores various research methodologies' in body_text, "Main content should be preserved"
    
    def test_date_not_duplicated_in_body(self):
        """Test that date extracted for metadata is not duplicated in document body."""
        document = {
            'metadata': {},
            'page_count': 1,
            'pages': [{
                'page_number': 1,
                'text': '''Technical Report

Development Team
January 15, 2024

This report summarizes the development progress.''',
            }]
        }
        
        # Extract metadata
        enhanced_document = document.copy()
        enhanced_document['metadata'] = self.extractor.extract_enhanced_metadata(document)
        
        # Generate LaTeX
        latex_output = self.generator.generate(enhanced_document)
        
        # Check body content
        lines = latex_output.split('\n')
        body_lines = []
        after_maketitle = False
        
        for line in lines:
            if '\\maketitle' in line:
                after_maketitle = True
                continue
            if after_maketitle:
                body_lines.append(line)
        
        body_text = '\n'.join(body_lines).strip()
        
        # Date should not appear standalone in the body if it was extracted as metadata
        extracted_date = enhanced_document['metadata'].get('date', '')
        if extracted_date and 'January 15, 2024' in extracted_date:
            assert 'January 15, 2024' not in body_text, "Date should not be duplicated in body"
        
        # Main content should still be present
        assert 'This report summarizes the development progress' in body_text, "Main content should be preserved"
    
    def test_complex_metadata_extraction_and_filtering(self):
        """Test complex case with title, author, and date all extracted and filtered."""
        document = {
            'metadata': {},
            'page_count': 1,
            'pages': [{
                'page_number': 1,
                'text': '''Advanced AI Research Paper

Dr. Alice Johnson and Prof. Bob Wilson
Stanford University
December 2023

Abstract

This paper presents groundbreaking research in artificial intelligence.

Introduction

Recent advances in machine learning have opened new possibilities.''',
            }]
        }
        
        # Extract metadata
        enhanced_document = document.copy()
        enhanced_document['metadata'] = self.extractor.extract_enhanced_metadata(document)
        
        # Generate LaTeX
        latex_output = self.generator.generate(enhanced_document)
        
        # Verify metadata commands are present
        assert '\\title{' in latex_output, "Title command should be present"
        assert '\\maketitle' in latex_output, "Maketitle command should be present"
        
        # Check body content
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
        
        # Main content sections should be present
        assert 'Abstract' in body_text or 'Introduction' in body_text, "Main content sections should be preserved"
        assert 'This paper presents groundbreaking research' in body_text, "Abstract content should be preserved"
        assert 'Recent advances in machine learning' in body_text, "Introduction content should be preserved"
        
        # Metadata should not be duplicated in body
        title = enhanced_document['metadata'].get('title', '')
        author = enhanced_document['metadata'].get('author', '')
        
        if title:
            # Check that title doesn't appear as a section (common duplication pattern)
            assert f'\\section{{{title}}}' not in body_text, "Title should not be duplicated as section"
        
        if author:
            # Check that author doesn't appear as a section
            assert f'\\section{{{author}}}' not in body_text, "Author should not be duplicated as section"
    
    def test_empty_body_after_metadata_removal(self):
        """Test case where all text is metadata, resulting in empty body."""
        document = {
            'metadata': {},
            'page_count': 1,
            'pages': [{
                'page_number': 1,
                'text': '''Simple Title
Author Name
2024''',
            }]
        }
        
        # Extract metadata
        enhanced_document = document.copy()
        enhanced_document['metadata'] = self.extractor.extract_enhanced_metadata(document)
        
        # Generate LaTeX
        latex_output = self.generator.generate(enhanced_document)
        
        # Should have metadata commands
        assert '\\title{' in latex_output, "Title command should be present"
        assert '\\maketitle' in latex_output, "Maketitle command should be present"
        
        # Body should be essentially empty (just closing document)
        lines = latex_output.split('\n')
        body_lines = []
        after_maketitle = False
        
        for line in lines:
            if '\\maketitle' in line:
                after_maketitle = True
                continue
            if after_maketitle and line.strip() and not line.strip().startswith('\\end{document}'):
                body_lines.append(line)
        
        # Should have very little or no body content
        body_text = '\n'.join(body_lines).strip()
        assert len(body_text) < 50, f"Body should be mostly empty, but got: '{body_text}'"


if __name__ == '__main__':
    # Run the tests
    test_class = TestMetadataDuplicationFix()
    test_class.setup_method()
    
    print("🧪 Testing Metadata Duplication Fix")
    print("=" * 60)
    
    try:
        test_class.test_title_not_duplicated_in_body()
        print("✅ Title duplication prevention: PASSED")
        
        test_class.test_author_not_duplicated_in_body()
        print("✅ Author duplication prevention: PASSED")
        
        test_class.test_date_not_duplicated_in_body()
        print("✅ Date duplication prevention: PASSED")
        
        test_class.test_complex_metadata_extraction_and_filtering()
        print("✅ Complex metadata filtering: PASSED")
        
        test_class.test_empty_body_after_metadata_removal()
        print("✅ Empty body handling: PASSED")
        
        print("\n🎉 All metadata duplication tests passed!")
        print("\nThe fix correctly:")
        print("  • Extracts title, author, and date for LaTeX metadata commands")
        print("  • Generates \\maketitle command")
        print("  • Removes extracted metadata from document body")
        print("  • Preserves actual document content")
        print("  • Handles edge cases like empty bodies")
        
    except AssertionError as e:
        print(f"❌ Test failed: {e}")
    except Exception as e:
        print(f"❌ Error running tests: {e}")
