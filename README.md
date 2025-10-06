# PDF to LaTeX Converter

Convert PDF documents to LaTeX source code while preserving formatting, structure, and mathematical expressions.

## Features

- Extract text, images, and formatting from PDF documents
- Generate clean, compilable LaTeX code
- Preserve document structure (sections, subsections, etc.)
- Handle mathematical expressions and equations
- Support for tables, figures, and references
- Command-line interface for easy usage

## Installation

```bash
pip install -e .
```

## Quick Start

```bash
# Convert a PDF to LaTeX
pdf2latex input.pdf output.tex

# With custom options
pdf2latex input.pdf output.tex --template article --preserve-images
```

## Development

```bash
# Install in development mode
pip install -e .[dev]

# Run tests
pytest

# Format code
black src/

# Type checking
mypy src/
```

## Project Structure

```
pdf2latex/
├── src/pdf2latex/          # Main package
│   ├── __init__.py
│   ├── cli.py              # Command-line interface
│   ├── converter.py        # Main converter class
│   ├── pdf_parser.py       # PDF parsing logic
│   ├── latex_generator.py  # LaTeX generation
│   └── utils/              # Utility modules
├── tests/                  # Test suite
├── docs/                   # Documentation
├── examples/               # Example files
└── requirements.txt        # Dependencies
```

## License

MIT License
