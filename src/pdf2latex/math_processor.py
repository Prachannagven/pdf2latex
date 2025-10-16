"""
Mathematical expression detection and conversion module.
Handles various mathematical notations and converts them to proper LaTeX math commands.
"""

import re
from typing import Dict, List, Tuple, Optional
from loguru import logger


class MathProcessor:
    """
    Processes mathematical expressions and converts them to LaTeX format.
    """
    
    def __init__(self):
        """Initialize the math processor with pattern definitions."""
        self.patterns = self._initialize_patterns()
        self.greek_letters = self._initialize_greek_letters()
        
    def _initialize_patterns(self) -> Dict[str, Dict]:
        """Initialize mathematical pattern definitions."""
        return {
            # Superscripts and subscripts
            'superscript': {
                'patterns': [
                    r'([a-zA-Z0-9\)])\^([a-zA-Z0-9\-\+]+)',  # x^2, E^-1
                    r'([a-zA-Z0-9\)])²',  # x², E²
                    r'([a-zA-Z0-9\)])³',  # x³, E³
                    r'([a-zA-Z0-9\)])([⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻]+)',  # Unicode superscripts
                    r'\)([0-9])\b',  # Trailing digits after parentheses: (VGS-Vth)2 → (VGS-Vth)^2
                ],
                'replacements': [
                    r'\1^{\2}',
                    r'\1^{2}',
                    r'\1^{3}',
                    lambda m: f'{m.group(1)}^{{{self._convert_unicode_superscript(m.group(2))}}}',
                    r')^{\1}'
                ]
            },
            
            'subscript': {
                'patterns': [
                    r'([a-zA-Z])_([a-zA-Z0-9\-\+]+)',  # x_i, H_2O
                    r'([a-zA-Z])([₀₁₂₃₄₅₆₇₈₉₊₋]+)',  # Unicode subscripts
                    r'\b([A-Z])([A-Z]{2,})\b',  # Common variables: VGS → V_{GS}, VTH → V_{TH}
                    r'\b([A-Z])([a-z]+)\b',  # Variables like Vth → V_{th}
                    r'\b([A-Z])([a-z]*[A-Z][a-z]*)\b',  # Variables like Cox → C_{ox}
                    r'\b(ID)\b',  # Specific case: ID → I_D
                    r'µ([a-z])([A-Z][a-z]*)',  # Pattern like µnCox → \mu_n C_{ox}
                ],
                'replacements': [
                    r'\1_{\2}',
                    lambda m: f'{m.group(1)}_{{{self._convert_unicode_subscript(m.group(2))}}}',
                    r'\1_{\2}',
                    r'\1_{\2}',  
                    r'\1_{\2}',
                    r'I_D',
                    r'\\mu_{\1} C_{\2}'
                ]
            },
            
            # Fractions
            'fractions': {
                'patterns': [
                    r'(\d+)/(\d+)',  # Simple fractions: 1/2, 3/4
                    r'\(([^)]+)\)/\(([^)]+)\)',  # Parenthesized fractions: (x+1)/(x-1)
                    r'\b([A-Z])/([A-Z])\b',  # Variable fractions: W/L → \frac{W}{L}
                ],
                'replacements': [
                    r'\\frac{\1}{\2}',
                    r'\\frac{\1}{\2}',
                    r'\\frac{\1}{\2}'
                ]
            },
            
            # Square roots
            'square_roots': {
                'patterns': [
                    r'√\(([^)]+)\)',  # √(expression)
                    r'√([a-zA-Z0-9]+)',  # √x, √25
                ],
                'replacements': [
                    r'\\sqrt{\1}',
                    r'\\sqrt{\1}'
                ]
            },
            
            # Mathematical operators
            'operators': {
                'patterns': [
                    r'±',  # Plus-minus
                    r'∓',  # Minus-plus
                    r'×',  # Multiplication
                    r'÷',  # Division
                    r'≤',  # Less than or equal
                    r'≥',  # Greater than or equal
                    r'≠',  # Not equal
                    r'≈',  # Approximately equal
                    r'∞',  # Infinity
                    r'∑',  # Sum
                    r'∏',  # Product
                    r'∫',  # Integral
                    r'∂',  # Partial derivative
                    r'∇',  # Nabla
                    r'∆',  # Delta
                    r'→',  # Right arrow
                    r'←',  # Left arrow
                ],
                'replacements': [
                    r'\\pm', r'\\mp', r'\\times', r'\\div',
                    r'\\leq', r'\\geq', r'\\neq', r'\\approx',
                    r'\\infty', r'\\sum', r'\\prod', r'\\int',
                    r'\\partial', r'\\nabla', r'\\Delta',
                    r'\\rightarrow', r'\\leftarrow'
                ]
            },
            
            # Common mathematical expressions
            'expressions': {
                'patterns': [
                    r'E\s*=\s*mc²',  # Einstein's equation
                    r'E\s*=\s*mc\^2',
                    r'a²\s*\+\s*b²\s*=\s*c²',  # Pythagorean theorem
                    r'a\^2\s*\+\s*b\^2\s*=\s*c\^2',
                    r'sin\(([^)]+)\)',  # Trigonometric functions
                    r'cos\(([^)]+)\)',
                    r'tan\(([^)]+)\)',
                    r'log\(([^)]+)\)',  # Logarithms
                    r'ln\(([^)]+)\)',
                    r'exp\(([^)]+)\)',  # Exponential
                ],
                'replacements': [
                    r'E = mc^{2}',
                    r'E = mc^{2}',
                    r'a^{2} + b^{2} = c^{2}',
                    r'a^{2} + b^{2} = c^{2}',
                    r'\\sin(\1)',
                    r'\\cos(\1)',
                    r'\\tan(\1)',
                    r'\\log(\1)',
                    r'\\ln(\1)',
                    r'\\exp(\1)'
                ]
            },
            
            # Specific equation patterns  
            'equation_reconstruction': {
                'patterns': [
                    r'([A-Z]+)\s*=\s*1\s*2([µμ][a-z]+[A-Z][a-z]*)\s*([A-Z])\s*([A-Z])\s*\(([A-Z]+)\s*[\-]\s*([A-Z][a-z]+)\)([0-9])',  # ID = 1 2µnCox W L (VGS -Vth)2
                ],
                'replacements': [
                    lambda m: f'{m.group(1).replace("ID", "I_D")} = \\frac{{1}}{{2}}\\mu_n C_{{ox}} \\frac{{{m.group(3)}}}{{{m.group(4)}}}({m.group(5).replace("VGS", "V_{GS}")} - {m.group(6).replace("Vth", "V_{th}")})'+'\\^{' + m.group(7) + '}'
                ]
            }
        }
    
    def _initialize_greek_letters(self) -> Dict[str, str]:
        """Initialize Greek letter mappings."""
        return {
            'α': r'\\alpha', 'β': r'\\beta', 'γ': r'\\gamma', 'δ': r'\\delta',
            'ε': r'\\epsilon', 'ζ': r'\\zeta', 'η': r'\\eta', 'θ': r'\\theta',
            'ι': r'\\iota', 'κ': r'\\kappa', 'λ': r'\\lambda', 'μ': r'\\mu', 'µ': r'\\mu',
            'ν': r'\\nu', 'ξ': r'\\xi', 'ο': r'\\omicron', 'π': r'\\pi',
            'ρ': r'\\rho', 'σ': r'\\sigma', 'τ': r'\\tau', 'υ': r'\\upsilon',
            'φ': r'\\phi', 'χ': r'\\chi', 'ψ': r'\\psi', 'ω': r'\\omega',
            'Α': r'\\Alpha', 'Β': r'\\Beta', 'Γ': r'\\Gamma', 'Δ': r'\\Delta',
            'Ε': r'\\Epsilon', 'Ζ': r'\\Zeta', 'Η': r'\\Eta', 'Θ': r'\\Theta',
            'Ι': r'\\Iota', 'Κ': r'\\Kappa', 'Λ': r'\\Lambda', 'Μ': r'\\Mu',
            'Ν': r'\\Nu', 'Ξ': r'\\Xi', 'Ο': r'\\Omicron', 'Π': r'\\Pi',
            'Ρ': r'\\Rho', 'Σ': r'\\Sigma', 'Τ': r'\\Tau', 'Υ': r'\\Upsilon',
            'Φ': r'\\Phi', 'Χ': r'\\Chi', 'Ψ': r'\\Psi', 'Ω': r'\\Omega'
        }
    
    def _convert_unicode_superscript(self, text: str) -> str:
        """Convert Unicode superscript characters to normal characters."""
        superscript_map = {
            '⁰': '0', '¹': '1', '²': '2', '³': '3', '⁴': '4', '⁵': '5',
            '⁶': '6', '⁷': '7', '⁸': '8', '⁹': '9', '⁺': '+', '⁻': '-'
        }
        result = text
        for sup, normal in superscript_map.items():
            result = result.replace(sup, normal)
        return result
    
    def _convert_unicode_subscript(self, text: str) -> str:
        """Convert Unicode subscript characters to normal characters."""
        subscript_map = {
            '₀': '0', '₁': '1', '₂': '2', '₃': '3', '₄': '4', '₅': '5',
            '₆': '6', '₇': '7', '₈': '8', '₉': '9', '₊': '+', '₋': '-'
        }
        result = text
        for sub, normal in subscript_map.items():
            result = result.replace(sub, normal)
        return result
    
    def detect_math_expressions(self, text: str) -> List[Dict]:
        """
        Detect mathematical expressions in text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            List of detected math expressions with positions and types
        """
        math_expressions = []
        
        # Check for various mathematical patterns
        for category, pattern_data in self.patterns.items():
            patterns = pattern_data['patterns']
            for i, pattern in enumerate(patterns):
                matches = re.finditer(pattern, text)
                for match in matches:
                    math_expressions.append({
                        'type': category,
                        'original': match.group(0),
                        'start': match.start(),
                        'end': match.end(),
                        'pattern_index': i,
                        'groups': match.groups()
                    })
        
        # Check for Greek letters
        for greek, latex in self.greek_letters.items():
            if greek in text:
                for match in re.finditer(re.escape(greek), text):
                    math_expressions.append({
                        'type': 'greek_letter',
                        'original': greek,
                        'latex': latex,
                        'start': match.start(),
                        'end': match.end()
                    })
        
        # Sort by position in text
        math_expressions.sort(key=lambda x: x['start'])
        
        logger.debug(f"Detected {len(math_expressions)} mathematical expressions")
        return math_expressions
    
    def convert_to_latex(self, text: str) -> str:
        """
        Convert mathematical expressions in text to LaTeX format.
        
        Args:
            text: Input text with mathematical expressions
            
        Returns:
            Text with mathematical expressions converted to LaTeX
        """
        result = text
        
        # Apply pattern-based conversions
        for category, pattern_data in self.patterns.items():
            patterns = pattern_data['patterns']
            replacements = pattern_data['replacements']
            
            for pattern, replacement in zip(patterns, replacements):
                if callable(replacement):
                    # Handle function-based replacements
                    result = re.sub(pattern, replacement, result)
                else:
                    result = re.sub(pattern, replacement, result)
        
        # Convert Greek letters
        for greek, latex in self.greek_letters.items():
            result = result.replace(greek, latex)
        
        return result
    
    def is_likely_math_line(self, text: str) -> bool:
        """
        Determine if a line of text likely contains mathematical content.
        
        Args:
            text: Text line to analyze
            
        Returns:
            True if the line likely contains mathematical expressions
        """
        # First, exclude obvious non-mathematical contexts
        text_lower = text.lower()
        
        # Exclude percentage contexts (like "85% response rate")
        if re.search(r'\d+\s*%\s+(?:response|increase|decrease|rate|growth|change)', text_lower):
            return False
        
        # Exclude statistical significance contexts (like "p < 0.05")
        if re.search(r'p\s*[<>]\s*0\.0\d+', text_lower):
            return False
        
        # Exclude time complexity contexts (like "O(n²)")
        if re.search(r'o\s*\([^)]*\)\s*time', text_lower):
            return False
        
        # Exclude version numbers and references (like "section 3.4", "version 2.1")
        if re.search(r'(?:section|chapter|version|figure|table|page)\s+\d+\.?\d*', text_lower):
            return False
        
        # Now check for mathematical indicators with better context
        strong_math_indicators = [
            r'[∑∏∫∂∇∆]',        # Strong mathematical symbols
            r'√\([^)]+\)',       # Square root with parentheses
            r'\b(sin|cos|tan|log|ln|exp)\s*\(',  # Mathematical functions with parentheses (word boundary required)
            r'\b[a-zA-Z]\s*[=]\s*[a-zA-Z0-9\^]+\s*[+\-*/]',  # Mathematical equations
            r'[a-zA-Z]\^[0-9]+\s*[+\-]',  # Clear algebraic expressions
            r'\d+/\d+\s*[+\-*/=]',  # Fractions in mathematical context
            r'[A-Z]\s*\([A-Z]{2,}\s*[\-]\s*[A-Z][a-z]+\)[0-9]',  # Pattern like "L (VGS -Vth)2"
            r'\d+[μµ][a-z]+[A-Z][a-z]*',  # Pattern like "2µnCox"
        ]
        
        # Strong indicators suggest it's definitely math
        for indicator in strong_math_indicators:
            if re.search(indicator, text):
                return True
        
        # Weaker indicators need more context
        weak_math_indicators = [
            r'[=<>≤≥≠≈]',      # Mathematical operators (but common in text)
            r'[α-ωΑ-Ω]',       # Greek letters (but used in regular text too)
            r'[²³⁰¹⁴⁵⁶⁷⁸⁹]',  # Unicode superscripts
            r'[₀₁₂₃₄₅₆₇₈₉]',    # Unicode subscripts
            r'\^[0-9\-\+]',     # Explicit superscripts
            r'_[0-9\-\+]',      # Explicit subscripts
            r'\([A-Z]{2,}[\-][A-Z][a-z]+\)',  # Pattern like "(VGS-Vth)"
            r'^[A-Z]$',        # Single capital letter (likely a variable)
            r'\d+[μµ]',        # Number with mu (micro)
            r'[A-Z]/[A-Z]',    # Variable ratios like W/L
        ]
        
        # Count weak indicators
        weak_matches = 0
        for indicator in weak_math_indicators:
            if re.search(indicator, text):
                weak_matches += 1
        
        # Multiple weak indicators or specific contexts suggest math
        if weak_matches >= 2:
            return True
        
        # Single weak indicator in short text (likely standalone equation)
        if weak_matches >= 1 and len(text.strip()) < 30 and not any(word in text_lower for word in ['the', 'and', 'or', 'in', 'on', 'at', 'to', 'for', 'with']):
            return True
        
        return False
    
    def wrap_math_expressions(self, text: str, inline_threshold: int = 50) -> str:
        """
        Wrap mathematical expressions in appropriate LaTeX math environments.
        
        Args:
            text: Text with converted mathematical expressions
            inline_threshold: Character threshold for inline vs display math
            
        Returns:
            Text with math expressions wrapped in LaTeX math environments
        """
        # Simple heuristic: if line is short and contains math, make it inline
        # If line is mostly math or long math expression, make it display
        
        if self.is_likely_math_line(text.strip()):
            clean_text = text.strip()
            
            # Check if it's a standalone equation
            if len(clean_text) < inline_threshold and not clean_text.endswith('.'):
                # Likely a standalone equation - use display math
                return f"\\[{clean_text}\\]"
            else:
                # Inline math within text
                return f"${clean_text}$"
        
        return text
