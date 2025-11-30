from pathlib import Path
import sys
sys.path.insert(0, 'src')

from pdf2latex.converter import PDF2LaTeXConverter

# Test with a different PDF
pdf_path = Path("/home/pranav/Documents/3-1-notes/commsys/compres/20-21 - CommSys - Compre 1.pdf")
output_path = Path("/tmp/20-21-test.tex")

converter = PDF2LaTeXConverter()
converter.convert(pdf_path, output_path)
print(f"Converted {pdf_path.name} to {output_path}")
print(f"Output size: {output_path.stat().st_size} bytes")
