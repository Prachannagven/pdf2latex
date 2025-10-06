"""
PDF to LaTeX Converter

A Python package for converting PDF documents to LaTeX source code,
preserving formatting, structure, and mathematical expressions.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .pdf_parser import PDFParser
from .latex_generator import LaTeXGenerator
from .converter import PDF2LaTeXConverter

__all__ = ["PDFParser", "LaTeXGenerator", "PDF2LaTeXConverter"]
