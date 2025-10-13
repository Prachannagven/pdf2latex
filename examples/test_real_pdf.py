#!/usr/bin/env python3
"""
Test the PDF2LaTeX converter with a real PDF file.
"""

import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pdf2latex import PDF2LaTeXConverter
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

console = Console()


def test_with_real_pdf(pdf_path: Path):
    """Test the converter with a real PDF file."""
    
    if not pdf_path.exists():
        console.print(f"[red]❌ PDF file not found: {pdf_path}[/red]")
        return
    
    console.print(Panel(f"🔄 Testing PDF2LaTeX Conversion\nFile: {pdf_path}", style="bold blue"))
    
    try:
        # Initialize converter
        converter = PDF2LaTeXConverter(template='article', preserve_images=True)
        
        console.print("\n[yellow]📖 Step 1: Parsing PDF...[/yellow]")
        
        # Parse the PDF
        document = converter.parse_pdf(pdf_path)
        
        # Show parsing results
        console.print(f"✅ Successfully parsed PDF")
        console.print(f"   • Parser used: {document.get('parser_used', 'unknown')}")
        console.print(f"   • Pages found: {document.get('page_count', 0)}")
        console.print(f"   • Title: {document.get('metadata', {}).get('title', 'No title')}")
        console.print(f"   • Author: {document.get('metadata', {}).get('author', 'No author')}")
        
        # Show first page content preview
        if document.get('pages'):
            first_page = document['pages'][0]
            text_preview = first_page.get('text', '')[:200] + '...' if len(first_page.get('text', '')) > 200 else first_page.get('text', '')
            console.print(f"   • First page preview: {text_preview}")
        
        console.print("\n[yellow]✍️  Step 2: Generating LaTeX...[/yellow]")
        
        # Generate LaTeX
        latex_content = converter.generate_latex(document)
        
        console.print(f"✅ Successfully generated LaTeX")
        console.print(f"   • Content length: {len(latex_content)} characters")
        console.print(f"   • Lines: {len(latex_content.split(chr(10)))}")
        
        # Save output
        output_path = pdf_path.with_suffix('.tex')
        output_path.write_text(latex_content, encoding='utf-8')
        
        console.print(f"\n[green]🎉 Conversion completed![/green]")
        console.print(f"   • Output saved to: {output_path}")
        
        # Show LaTeX preview
        console.print("\n[yellow]📄 LaTeX Preview (first 30 lines):[/yellow]")
        latex_lines = latex_content.split('\n')[:30]
        latex_preview = '\n'.join(latex_lines)
        
        syntax = Syntax(latex_preview, "latex", theme="monokai", line_numbers=True)
        console.print(syntax)
        
        if len(latex_content.split('\n')) > 30:
            console.print(f"[dim]... and {len(latex_content.split(chr(10))) - 30} more lines[/dim]")
        
        console.print(f"\n[blue]🔨 To compile LaTeX:[/blue]")
        console.print(f"   cd {output_path.parent}")
        console.print(f"   pdflatex {output_path.name}")
        
        return output_path
        
    except Exception as e:
        console.print(f"[red]❌ Conversion failed: {e}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        return None


def main():
    """Main function."""
    if len(sys.argv) != 2:
        console.print("[yellow]Usage: python test_real_pdf.py <pdf_file>[/yellow]")
        console.print("\n[blue]Examples:[/blue]")
        console.print("  python test_real_pdf.py sample.pdf")
        console.print("  python test_real_pdf.py /path/to/document.pdf")
        return
    
    pdf_path = Path(sys.argv[1])
    test_with_real_pdf(pdf_path)


if __name__ == '__main__':
    main()
