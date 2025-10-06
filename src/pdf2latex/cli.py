#!/usr/bin/env python3
"""
Command-line interface for PDF to LaTeX converter.
"""

import click
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from loguru import logger
import sys

from .converter import PDF2LaTeXConverter

console = Console()


@click.command()
@click.argument('input_pdf', type=click.Path(exists=True, path_type=Path))
@click.argument('output_tex', type=click.Path(path_type=Path))
@click.option('--template', '-t', default='article', 
              help='LaTeX document template (article, report, book)')
@click.option('--preserve-images/--no-images', default=True,
              help='Include images in the output')
@click.option('--verbose', '-v', is_flag=True,
              help='Enable verbose output')
@click.option('--debug', is_flag=True,
              help='Enable debug mode')
@click.version_option()
def main(input_pdf: Path, output_tex: Path, template: str, 
         preserve_images: bool, verbose: bool, debug: bool):
    """
    Convert PDF documents to LaTeX source code.
    
    INPUT_PDF: Path to the input PDF file
    OUTPUT_TEX: Path to the output LaTeX file
    """
    # Configure logging
    if debug:
        logger.add(sys.stderr, level="DEBUG")
    elif verbose:
        logger.add(sys.stderr, level="INFO")
    else:
        logger.add(sys.stderr, level="WARNING")
    
    console.print(f"[bold blue]PDF to LaTeX Converter[/bold blue]")
    console.print(f"Input:  {input_pdf}")
    console.print(f"Output: {output_tex}")
    console.print(f"Template: {template}")
    console.print()
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            # Initialize converter
            task = progress.add_task("Initializing converter...", total=None)
            converter = PDF2LaTeXConverter(
                template=template,
                preserve_images=preserve_images
            )
            
            # Parse PDF
            progress.update(task, description="Parsing PDF document...")
            document = converter.parse_pdf(input_pdf)
            
            # Generate LaTeX
            progress.update(task, description="Generating LaTeX code...")
            latex_content = converter.generate_latex(document)
            
            # Write output
            progress.update(task, description="Writing output file...")
            output_tex.write_text(latex_content, encoding='utf-8')
            
            progress.update(task, description="✅ Conversion completed!")
        
        console.print(f"[bold green]Success![/bold green] LaTeX file saved to: {output_tex}")
        
        # Show basic stats
        with open(input_pdf, 'rb') as f:
            pdf_size = len(f.read())
        latex_size = len(latex_content.encode('utf-8'))
        
        console.print(f"\n[dim]Statistics:[/dim]")
        console.print(f"  PDF size: {pdf_size:,} bytes")
        console.print(f"  LaTeX size: {latex_size:,} bytes")
        console.print(f"  Pages processed: {document.page_count if hasattr(document, 'page_count') else 'N/A'}")
        
    except Exception as e:
        logger.error(f"Conversion failed: {e}")
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
