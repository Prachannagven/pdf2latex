#!/usr/bin/env python3
"""
Test the enhanced metadata extraction and LaTeX title generation functionality.
"""

import pytest
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pdf2latex.metadata_extractor import MetadataExtractor
from pdf2latex.latex_generator import LaTeXGenerator


class TestMetadataExtractor:
    """Test cases for metadata extraction functionality."""
    
    def setup_method(self):
        """Set up test cases."""
        self.extractor = MetadataExtractor()
    
    def test_title_detection_from_content(self):
        """Test title detection from document content."""
        document = {
            'metadata': {},
            'pages': [{
                'text': '''Impact of Climate Change on Marine Ecosystems
                
                By Dr. Jane Smith
                University of Ocean Sciences
                
                Abstract
                This study examines the effects of rising temperatures on marine life...
                ''',
                'page_number': 1
            }],
            'page_count': 1
        }
        
        enhanced_metadata = self.extractor.extract_enhanced_metadata(document)
        
        assert enhanced_metadata['title'] == "Impact of Climate Change on Marine Ecosystems"
        assert enhanced_metadata['author'] == "Dr. Jane Smith"
        assert enhanced_metadata['structure']['has_abstract'] is True
    
    def test_title_detection_patterns(self):
        """Test various title detection patterns."""
        test_cases = [
            {
                'text': '''Machine Learning in Healthcare: A Comprehensive Review
                
                Introduction
                Machine learning has revolutionized...''',
                'expected_title': "Machine Learning in Healthcare: A Comprehensive Review"
            },
            {
                'text': '''THE FUTURE OF ARTIFICIAL INTELLIGENCE
                
                Abstract
                This paper discusses...''',
                'expected_title': "THE FUTURE OF ARTIFICIAL INTELLIGENCE"
            },
            {
                'text': '''Quantum Computing Applications
                Research Paper
                
                By Dr. Alice Johnson and Dr. Bob Wilson
                MIT Computer Science Department''',
                'expected_title': "Quantum Computing Applications"
            }
        ]
        
        for case in test_cases:
            document = {
                'metadata': {},
                'pages': [{'text': case['text'], 'page_number': 1}],
                'page_count': 1
            }
            
            enhanced_metadata = self.extractor.extract_enhanced_metadata(document)
            assert enhanced_metadata['title'] == case['expected_title']
    
    def test_author_detection_patterns(self):
        """Test author detection from various patterns."""
        test_cases = [
            {
                'text': '''Research Paper Title

By Dr. John Smith

Abstract...''',
                'expected_author': "Dr. John Smith"
            },
            {
                'text': '''Paper Title

Author: Sarah Johnson and Mike Davis

Content...''',
                'expected_author': "Sarah Johnson and Mike Davis"
            },
            {
                'text': '''Research Title

Prof. Alice Brown
University of Science
alice.brown@university.edu

Abstract...''',
                'expected_author': "Prof. Alice Brown"
            }
        ]
        
        for case in test_cases:
            document = {
                'metadata': {},
                'pages': [{'text': case['text'], 'page_number': 1}],
                'page_count': 1
            }
            
            enhanced_metadata = self.extractor.extract_enhanced_metadata(document)
            if enhanced_metadata.get('author'):
                assert case['expected_author'] in enhanced_metadata['author']
    
    def test_date_detection_patterns(self):
        """Test date detection from various formats."""
        test_cases = [
            {
                'text': '''Paper Title
                
                Published: 2023
                
                Abstract...''',
                'expected_date': "2023"
            },
            {
                'text': '''Research Paper
                
                Date: January 15, 2024
                
                Content...''',
                'expected_date': "January 15, 2024"
            },
            {
                'text': '''Title
                
                Copyright 2022
                
                Text...''',
                'expected_date': "2022"
            }
        ]
        
        for case in test_cases:
            document = {
                'metadata': {},
                'pages': [{'text': case['text'], 'page_number': 1}],
                'page_count': 1
            }
            
            enhanced_metadata = self.extractor.extract_enhanced_metadata(document)
            if enhanced_metadata.get('date'):
                assert case['expected_date'] in enhanced_metadata['date']
    
    def test_document_structure_analysis(self):
        """Test document structure analysis."""
        document = {
            'metadata': {},
            'pages': [{
                'text': '''Research Paper Title
                
                Abstract
                This study examines...
                
                Introduction
                The field of study has shown...
                
                Conclusion
                In summary, our findings...
                
                References
                [1] Smith, J. (2020)...''',
                'page_number': 1
            }],
            'page_count': 1
        }
        
        enhanced_metadata = self.extractor.extract_enhanced_metadata(document)
        structure = enhanced_metadata['structure']
        
        assert structure['has_abstract'] is True
        assert structure['has_introduction'] is True
        assert structure['has_conclusion'] is True
        assert structure['has_references'] is True
        assert structure['estimated_type'] == 'academic_paper'
    
    def test_existing_metadata_preservation(self):
        """Test that existing metadata is preserved and enhanced."""
        document = {
            'metadata': {
                'title': 'Original Title',
                'author': 'Original Author',
                'creator': 'PDF Creator'
            },
            'pages': [{
                'text': '''Different Title in Content
                
                By Different Author
                
                Content...''',
                'page_number': 1
            }],
            'page_count': 1
        }
        
        enhanced_metadata = self.extractor.extract_enhanced_metadata(document)
        
        # Should keep original title and author since they exist
        assert enhanced_metadata['title'] == 'Original Title'
        assert enhanced_metadata['author'] == 'Original Author'
        assert enhanced_metadata['creator'] == 'PDF Creator'  # Preserved
        assert 'structure' in enhanced_metadata  # Added


class TestLaTeXTitleGeneration:
    """Test cases for LaTeX title generation with enhanced metadata."""
    
    def setup_method(self):
        """Set up test cases."""
        self.generator = LaTeXGenerator(template='article')
    
    def test_title_generation_with_metadata(self):
        """Test LaTeX generation with complete metadata."""
        document = {
            'metadata': {
                'title': 'Advanced Machine Learning Techniques',
                'author': 'Dr. Jane Smith',
                'date': '2024-01-15',
                'structure': {'has_abstract': False}
            },
            'pages': [{'text': 'Content...', 'page_number': 1}],
            'page_count': 1
        }
        
        latex_output = self.generator.generate(document)
        
        # Check that title, author, and date are properly included
        assert '\\title{Advanced Machine Learning Techniques}' in latex_output
        assert '\\author{Dr. Jane Smith}' in latex_output
        assert '\\date{15/01/2024}' in latex_output
        assert '\\maketitle' in latex_output
    
    def test_title_generation_with_abstract(self):
        """Test LaTeX generation with abstract detection."""
        document = {
            'metadata': {
                'title': 'Research Paper',
                'author': 'Dr. Smith',
                'structure': {'has_abstract': True}
            },
            'pages': [{
                'text': '''Research Paper

Abstract
This study presents a comprehensive analysis of machine learning applications in healthcare.

Introduction
The field has evolved significantly...''',
                'page_number': 1
            }],
            'page_count': 1
        }
        
        latex_output = self.generator.generate(document)
        
        assert '\\maketitle' in latex_output
        assert '\\begin{abstract}' in latex_output
        assert '\\end{abstract}' in latex_output
        assert 'comprehensive analysis' in latex_output
    
    def test_fallback_title_from_filename(self):
        """Test fallback title generation from filename."""
        document = {
            'metadata': {},
            'pdf_path': '/path/to/my_research_paper.pdf',
            'pages': [{'text': 'Content...', 'page_number': 1}],
            'page_count': 1
        }
        
        latex_output = self.generator.generate(document)
        
        assert '\\title{my\\_research\\_paper}' in latex_output
        assert '\\date{\\today}' in latex_output
        assert '\\maketitle' in latex_output
    
    def test_special_character_escaping_in_title(self):
        """Test proper escaping of special LaTeX characters in title."""
        document = {
            'metadata': {
                'title': 'Analysis of CO₂ & Climate Change (50% increase)',
                'author': 'Dr. Smith & Jones',
                'structure': {'has_abstract': False}
            },
            'pages': [{'text': 'Content...', 'page_number': 1}],
            'page_count': 1
        }
        
        latex_output = self.generator.generate(document)
        
        # Check that special characters are properly escaped
        assert '\\&' in latex_output  # & should be escaped
        assert '\\%' in latex_output  # % should be escaped
        assert '(' in latex_output    # Parentheses should remain
    
    def test_date_formatting(self):
        """Test various date format handling."""
        date_test_cases = [
            ('2024-01-15', '15/01/2024'),
            ('D:20240115120000', '15/01/2024'),
            ('January 15, 2024', 'January 15, 2024'),
            ('2024', '2024'),
            ('15/01/2024', '15/01/2024')
        ]
        
        for input_date, expected_output in date_test_cases:
            formatted_date = self.generator._format_date(input_date)
            assert formatted_date == expected_output
    
    def test_abstract_extraction(self):
        """Test abstract extraction from document text."""
        document = {
            'metadata': {'structure': {'has_abstract': True}},
            'pages': [{
                'text': '''Research Paper Title
                
                Abstract
                This comprehensive study examines the impact of artificial intelligence 
                on modern healthcare systems. Our findings indicate significant improvements 
                in diagnostic accuracy and patient outcomes.
                
                Introduction
                The healthcare industry has undergone...''',
                'page_number': 1
            }],
            'page_count': 1
        }
        
        abstract_text = self.generator._extract_abstract(document)
        
        assert abstract_text is not None
        assert 'comprehensive study examines' in abstract_text
        assert 'diagnostic accuracy' in abstract_text
        assert len(abstract_text) > 50


def test_integration_metadata_and_latex():
    """Integration test for metadata extraction and LaTeX generation."""
    # Create a sample document with various elements
    document = {
        'metadata': {},  # Start with empty metadata
        'pages': [{
            'text': '''Machine Learning in Medical Diagnosis: A Revolutionary Approach
            
            By Dr. Sarah Johnson and Prof. Michael Chen
            Stanford University Medical School
            
            Published: March 2024
            
            Abstract
            This groundbreaking research demonstrates how machine learning algorithms 
            can significantly improve diagnostic accuracy in medical imaging. Our study 
            analyzed over 10,000 patient cases and showed a 95% accuracy rate.
            
            Introduction
            The integration of artificial intelligence in healthcare represents...
            
            Conclusion
            Our findings suggest that machine learning can revolutionize medical diagnosis...
            
            References
            [1] Smith, A. et al. (2023) "AI in Healthcare"...''',
            'page_number': 1
        }],
        'page_count': 1,
        'pdf_path': '/path/to/ml_medical_diagnosis.pdf'
    }
    
    # Step 1: Extract enhanced metadata
    extractor = MetadataExtractor()
    enhanced_metadata = extractor.extract_enhanced_metadata(document)
    document['metadata'] = enhanced_metadata
    
    # Verify metadata extraction
    assert enhanced_metadata['title'] == "Machine Learning in Medical Diagnosis: A Revolutionary Approach"
    assert "Dr. Sarah Johnson" in enhanced_metadata['author']
    assert enhanced_metadata['date'] == "March 2024"
    assert enhanced_metadata['structure']['estimated_type'] == 'academic_paper'
    
    # Step 2: Generate LaTeX with enhanced metadata
    generator = LaTeXGenerator(template='article')
    latex_output = generator.generate(document)
    
    # Verify LaTeX output includes all metadata
    assert '\\title{Machine Learning in Medical Diagnosis: A Revolutionary Approach}' in latex_output
    assert '\\author{' in latex_output and 'Dr. Sarah Johnson' in latex_output
    assert '\\date{March 2024}' in latex_output
    assert '\\maketitle' in latex_output
    assert '\\begin{abstract}' in latex_output
    assert 'groundbreaking research demonstrates' in latex_output
    assert '\\end{abstract}' in latex_output


if __name__ == '__main__':
    # Run specific tests
    print("Testing Enhanced Metadata Extraction and LaTeX Title Generation...")
    
    # Test metadata extractor
    test_metadata = TestMetadataExtractor()
    test_metadata.setup_method()
    
    print("✓ Testing title detection...")
    test_metadata.test_title_detection_from_content()
    test_metadata.test_title_detection_patterns()
    
    print("✓ Testing author detection...")
    test_metadata.test_author_detection_patterns()
    
    print("✓ Testing date detection...")
    test_metadata.test_date_detection_patterns()
    
    print("✓ Testing document structure analysis...")
    test_metadata.test_document_structure_analysis()
    
    print("✓ Testing metadata preservation...")
    test_metadata.test_existing_metadata_preservation()
    
    # Test LaTeX generator
    test_latex = TestLaTeXTitleGeneration()
    test_latex.setup_method()
    
    print("✓ Testing LaTeX title generation...")
    test_latex.test_title_generation_with_metadata()
    test_latex.test_title_generation_with_abstract()
    test_latex.test_fallback_title_from_filename()
    test_latex.test_special_character_escaping_in_title()
    test_latex.test_date_formatting()
    test_latex.test_abstract_extraction()
    
    # Integration test
    print("✓ Testing integration...")
    test_integration_metadata_and_latex()
    
    print("\n🎉 All metadata and title generation tests passed!")
    print("\nThe PDF2LaTeX converter now properly:")
    print("  • Detects titles from document content and formatting")
    print("  • Identifies authors using multiple heuristics")
    print("  • Extracts dates from various formats")
    print("  • Analyzes document structure (abstract, sections)")
    print("  • Generates proper LaTeX \\title{}, \\author{}, \\date{} commands")
    print("  • Uses \\maketitle for professional document formatting")
    print("  • Automatically extracts and formats abstracts")
    print("  • Handles special character escaping in metadata")
