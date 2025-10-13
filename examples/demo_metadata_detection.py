#!/usr/bin/env python3
"""
Demonstration of Enhanced Title and Metadata Detection
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pdf2latex import PDF2LaTeXConverter
from pdf2latex.metadata_extractor import MetadataExtractor
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

def demo_title_and_metadata():
    """Demonstrate the enhanced title and metadata detection capabilities."""
    
    console.print(Panel.fit(
        "[bold blue]🔍 Enhanced Title & Metadata Detection Demo[/bold blue]",
        border_style="blue"
    ))
    
    # Create sample documents with various title/metadata patterns
    test_documents = [
        {
            'name': 'Academic Paper',
            'content': '''Machine Learning in Healthcare: A Revolutionary Approach

By Dr. Sarah Johnson and Prof. Michael Chen
Stanford University Medical School

Published: March 2024

Abstract
This groundbreaking research demonstrates how machine learning algorithms 
can significantly improve diagnostic accuracy in medical imaging. Our study 
analyzed over 10,000 patient cases and showed a 95% accuracy rate.

Introduction
The integration of artificial intelligence in healthcare represents...''',
            'pdf_path': '/path/to/ml_healthcare_paper.pdf'
        },
        {
            'name': 'Technical Report',
            'content': '''QUANTUM COMPUTING APPLICATIONS IN CRYPTOGRAPHY

Author: Dr. Alice Johnson
Date: January 15, 2024

Summary
This report examines the potential impact of quantum computing on modern 
cryptographic systems and proposes new quantum-resistant algorithms.

Background
Current encryption methods rely on mathematical problems...''',
            'pdf_path': '/path/to/quantum_crypto_report.pdf'
        },
        {
            'name': 'Research Paper',
            'content': '''Impact of Climate Change on Marine Ecosystems

Prof. Robert Smith, Dr. Lisa Wilson
University of Ocean Sciences
robert.smith@oceanuni.edu

Copyright 2023

This study presents comprehensive data on temperature changes in ocean 
environments and their effects on marine biodiversity over the past decade.''',
            'pdf_path': '/path/to/climate_marine_study.pdf'
        },
        {
            'name': 'Minimal Metadata',
            'content': '''Basic Document

This is a simple document with minimal formatting.
It should still get proper LaTeX formatting.''',
            'pdf_path': '/path/to/simple_document.pdf'
        }
    ]
    
    # Initialize components
    extractor = MetadataExtractor()
    converter = PDF2LaTeXConverter(template='article', preserve_images=True)
    
    for i, doc_info in enumerate(test_documents, 1):
        console.print(f"\n[bold cyan]📄 Document {i}: {doc_info['name']}[/bold cyan]")
        
        # Create mock document structure
        document = {
            'metadata': {},  # Start with empty metadata
            'pages': [{
                'text': doc_info['content'],
                'page_number': 1
            }],
            'page_count': 1,
            'pdf_path': doc_info['pdf_path']
        }
        
        # Extract enhanced metadata
        enhanced_metadata = extractor.extract_enhanced_metadata(document)
        document['metadata'] = enhanced_metadata
        
        # Create results table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Property", style="cyan", no_wrap=True)
        table.add_column("Detected Value", style="white")
        table.add_column("Quality", style="green")
        
        # Add metadata rows
        title = enhanced_metadata.get('title', 'Not detected')
        author = enhanced_metadata.get('author', 'Not detected')
        date = enhanced_metadata.get('date', 'Not detected')
        structure_type = enhanced_metadata.get('structure', {}).get('estimated_type', 'document')
        quality_score = enhanced_metadata.get('quality_score', 0.0)
        
        table.add_row("Title", title[:60] + "..." if len(title) > 60 else title, "✓" if title != 'Not detected' else "✗")
        table.add_row("Author", author[:50] + "..." if len(author) > 50 else author, "✓" if author != 'Not detected' else "✗")
        table.add_row("Date", date, "✓" if date != 'Not detected' else "✗")
        table.add_row("Type", structure_type.replace('_', ' ').title(), "✓")
        table.add_row("Quality Score", f"{quality_score:.1%}", "✓" if quality_score > 0.5 else "⚠")
        
        console.print(table)
        
        # Generate LaTeX and show key parts
        latex_output = converter.generate_latex(document)
        
        console.print("\n[yellow]📝 Generated LaTeX Structure:[/yellow]")
        lines = latex_output.split('\n')
        
        # Extract and display key LaTeX commands
        for line in lines:
            if any(cmd in line for cmd in ['\\title{', '\\author{', '\\date{', '\\maketitle', '\\begin{abstract}', '\\end{abstract}']):
                if len(line.strip()) > 80:
                    console.print(f"  {line.strip()[:80]}...")
                else:
                    console.print(f"  {line.strip()}")
        
        # Show document structure features
        structure = enhanced_metadata.get('structure', {})
        features = []
        if structure.get('has_abstract'):
            features.append("Abstract")
        if structure.get('has_introduction'):
            features.append("Introduction")
        if structure.get('has_conclusion'):
            features.append("Conclusion")
        if structure.get('has_references'):
            features.append("References")
        
        if features:
            console.print(f"[green]📋 Detected Sections: {', '.join(features)}[/green]")
        
        console.print("─" * 80)
    
    # Summary
    console.print(Panel.fit(
        """[bold green]✅ Enhanced Metadata Detection Summary[/bold green]

The PDF2LaTeX converter now includes:
• [cyan]Intelligent title detection[/cyan] from document content and formatting
• [cyan]Multi-pattern author recognition[/cyan] (names, titles, affiliations)
• [cyan]Flexible date extraction[/cyan] from various formats
• [cyan]Document structure analysis[/cyan] (abstract, sections, references)
• [cyan]Professional LaTeX formatting[/cyan] with \\title{}, \\author{}, \\date{}
• [cyan]Automatic \\maketitle generation[/cyan] for proper document headers
• [cyan]Abstract extraction and formatting[/cyan] when detected
• [cyan]Quality scoring[/cyan] for metadata confidence assessment

[bold]Key Improvements:[/bold]
• Handles documents with missing or incomplete PDF metadata
• Uses content analysis and formatting heuristics for detection
• Generates properly structured LaTeX documents with titles
• Supports multiple document types (papers, reports, articles)
• Provides fallback mechanisms (filename → title, today → date)""",
        border_style="green"
    ))


if __name__ == '__main__':
    demo_title_and_metadata()
