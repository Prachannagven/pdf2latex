"""
Image extraction and processing module.
Extracts images from PDFs and prepares them for LaTeX inclusion.
"""

import fitz  # PyMuPDF
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from loguru import logger
import hashlib
from PIL import Image
import io


class ImageProcessor:
    """
    Processes images from PDFs and prepares them for LaTeX inclusion.
    """
    
    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize the image processor.
        
        Args:
            output_dir: Directory to save extracted images
        """
        self.output_dir = output_dir or Path("images")
        self.output_dir.mkdir(exist_ok=True)
        
        # Supported image formats for LaTeX
        self.supported_formats = {'.png', '.jpg', '.jpeg', '.pdf', '.eps'}
        
        logger.info(f"Initialized ImageProcessor with output directory: {self.output_dir}")
    
    def extract_images_from_page(self, page: fitz.Page, page_num: int, 
                                doc_hash: str, extracted_hashes: Optional[set] = None) -> List[Dict]:
        """
        Extract all images from a PDF page.
        
        Args:
            page: PyMuPDF page object
            page_num: Page number (1-based)
            doc_hash: Unique hash for the document
            extracted_hashes: Set of already extracted image hashes (for deduplication)
            
        Returns:
            List of image information dictionaries
        """
        if extracted_hashes is None:
            extracted_hashes = set()
        
        images = []
        unique_images = {}  # Map xref to image info to deduplicate within page
        image_list = page.get_images()
        
        logger.debug(f"Found {len(image_list)} image references on page {page_num}")
        
        for img_index, img in enumerate(image_list):
            try:
                # Extract image data
                xref = img[0]
                
                # Check if we've already processed this xref on this page
                if xref in unique_images:
                    logger.debug(f"Skipping duplicate xref {xref} on page {page_num}")
                    continue
                
                pix = fitz.Pixmap(page.parent, xref)
                
                # Skip images with unsupported color spaces
                if pix.n - pix.alpha >= 4:  # CMYK or higher
                    logger.warning(f"Skipping image {img_index} on page {page_num}: unsupported color space")
                    pix = None
                    continue
                
                # Convert RGBA to RGB if necessary
                if pix.alpha:
                    pix = fitz.Pixmap(fitz.csRGB, pix)
                
                # Generate unique hash based on image content
                image_hash = hashlib.md5(pix.tobytes()).hexdigest()[:8]
                
                # Check if we've already extracted this exact image
                if image_hash in extracted_hashes:
                    logger.debug(f"Skipping duplicate image {image_hash} on page {page_num}")
                    pix = None
                    continue
                
                # Add to extracted set
                extracted_hashes.add(image_hash)
                
                # Generate unique filename
                filename = f"{doc_hash}_p{page_num}_{img_index}_{image_hash}.png"
                image_path = self.output_dir / filename
                
                # Save image
                pix.save(str(image_path))
                
                # Get image dimensions and properties
                image_info = {
                    'filename': filename,
                    'path': image_path,
                    'page_number': page_num,
                    'index': img_index,
                    'width': pix.width,
                    'height': pix.height,
                    'colorspace': pix.colorspace.name if pix.colorspace else 'unknown',
                    'size_bytes': len(pix.tobytes()),
                    'bbox': page.get_image_bbox(img),  # Bounding box on page
                    'xref': xref
                }
                
                # Try to optimize the image
                try:
                    optimized_path = self._optimize_image(image_path, image_info)
                    if optimized_path != image_path:
                        image_info['path'] = optimized_path
                        image_info['filename'] = optimized_path.name
                except Exception as e:
                    logger.warning(f"Failed to optimize image {filename}: {e}")
                
                images.append(image_info)
                unique_images[xref] = image_info
                logger.debug(f"Extracted unique image: {filename} ({pix.width}x{pix.height})")
                
                pix = None  # Free memory
                
            except Exception as e:
                logger.error(f"Failed to extract image {img_index} from page {page_num}: {e}")
                continue
        
        if len(image_list) > len(images):
            logger.info(f"Deduplicated {len(image_list) - len(images)} duplicate images on page {page_num}")
        
        return images
    
    def _optimize_image(self, image_path: Path, image_info: Dict) -> Path:
        """
        Optimize image for LaTeX usage.
        
        Args:
            image_path: Path to the original image
            image_info: Image information dictionary
            
        Returns:
            Path to the optimized image
        """
        try:
            with Image.open(image_path) as img:
                # Check if optimization is needed
                if img.format == 'PNG' and image_info['size_bytes'] > 1024 * 1024:  # > 1MB
                    # Try JPEG conversion for large images
                    jpeg_path = image_path.with_suffix('.jpg')
                    
                    # Convert to RGB if necessary
                    if img.mode in ('RGBA', 'LA', 'P'):
                        # Create white background
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                        img = background
                    
                    # Save as JPEG with high quality
                    img.save(jpeg_path, 'JPEG', quality=85, optimize=True)
                    
                    # Check if JPEG is smaller
                    if jpeg_path.stat().st_size < image_path.stat().st_size * 0.8:
                        image_path.unlink()  # Remove original PNG
                        logger.debug(f"Optimized {image_path.name} -> {jpeg_path.name}")
                        return jpeg_path
                    else:
                        jpeg_path.unlink()  # Remove JPEG, keep PNG
                
                return image_path
                
        except Exception as e:
            logger.warning(f"Image optimization failed for {image_path}: {e}")
            return image_path
    
    def generate_latex_figure(self, image_info: Dict, caption: Optional[str] = None,
                            label: Optional[str] = None, width_ratio: float = 0.8,
                            placement: str = "H") -> str:
        """
        Generate LaTeX code for including an image.
        
        Args:
            image_info: Image information dictionary
            caption: Figure caption
            label: Figure label for referencing
            width_ratio: Width as fraction of text width
            placement: Figure placement options
            
        Returns:
            LaTeX code for the figure
        """
        filename = image_info['filename']
        
        # Generate caption if not provided
        if caption is None:
            caption = f"Image from page {image_info['page_number']}"
        
        # Generate label if not provided
        if label is None:
            label = f"fig:p{image_info['page_number']}_img{image_info['index']}"
        
        # Determine appropriate width
        if width_ratio > 1.0:
            width_ratio = 1.0
        elif width_ratio < 0.1:
            width_ratio = 0.1
        
        latex_code = f"""\\begin{{figure}}[{placement}]
    \\centering
    \\includegraphics[width={width_ratio}\\textwidth]{{{filename}}}
    \\caption{{{caption}}}
    \\label{{{label}}}
\\end{{figure}}"""
        
        return latex_code
    
    def generate_inline_image(self, image_info: Dict, width: Optional[str] = None) -> str:
        """
        Generate LaTeX code for an inline image.
        
        Args:
            image_info: Image information dictionary
            width: Custom width specification
            
        Returns:
            LaTeX code for inline image
        """
        filename = image_info['filename']
        
        if width is None:
            # Calculate appropriate width based on image dimensions
            if image_info['width'] > 600:
                width = "0.8\\textwidth"
            elif image_info['width'] > 300:
                width = "0.5\\textwidth"
            else:
                width = "0.3\\textwidth"
        
        return f"\\includegraphics[width={width}]{{{filename}}}"
    
    def analyze_image_placement(self, image_info: Dict, page_text: str) -> Dict:
        """
        Analyze where an image should be placed in the document.
        
        Args:
            image_info: Image information dictionary
            page_text: Text content of the page
            
        Returns:
            Placement analysis results
        """
        bbox = image_info.get('bbox', fitz.Rect())
        
        # Simple heuristics for image placement
        analysis = {
            'is_large': image_info['width'] > 400 or image_info['height'] > 400,
            'is_small': image_info['width'] < 200 and image_info['height'] < 200,
            'aspect_ratio': image_info['width'] / image_info['height'],
            'placement_suggestion': 'H',  # Default: Here
            'width_suggestion': 0.8,
            'is_likely_figure': True,
            'is_likely_inline': False
        }
        
        # Adjust suggestions based on size
        if analysis['is_large']:
            analysis['placement_suggestion'] = 'p'  # Full page
            analysis['width_suggestion'] = 0.9
        elif analysis['is_small']:
            analysis['is_likely_inline'] = True
            analysis['width_suggestion'] = 0.3
        
        # Adjust based on aspect ratio
        if analysis['aspect_ratio'] > 2.0:  # Very wide
            analysis['width_suggestion'] = 1.0
        elif analysis['aspect_ratio'] < 0.5:  # Very tall
            analysis['width_suggestion'] = 0.6
        
        return analysis
    
    def create_image_directory_structure(self, base_path: Path) -> None:
        """
        Create organized directory structure for images.
        
        Args:
            base_path: Base path for the document
        """
        doc_name = base_path.stem
        image_dir = base_path.parent / f"{doc_name}_images"
        image_dir.mkdir(exist_ok=True)
        
        # Update output directory
        self.output_dir = image_dir
        
        logger.info(f"Created image directory: {image_dir}")
    
    def get_document_hash(self, pdf_path: Path) -> str:
        """
        Generate a unique hash for the PDF document.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Document hash string
        """
        # Use file path and modification time for uniqueness
        content = f"{pdf_path.absolute()}_{pdf_path.stat().st_mtime}"
        return hashlib.md5(content.encode()).hexdigest()[:8]
    
    def extract_all_images(self, pdf_path: Path) -> Dict[int, List[Dict]]:
        """
        Extract all images from a PDF document.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary mapping page numbers to lists of image info
        """
        logger.info(f"Extracting images from: {pdf_path}")
        
        # Create organized directory structure
        self.create_image_directory_structure(pdf_path)
        
        # Generate document hash
        doc_hash = self.get_document_hash(pdf_path)
        
        all_images = {}
        extracted_hashes = set()  # Track extracted image hashes across all pages
        
        try:
            doc = fitz.open(pdf_path)
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_images = self.extract_images_from_page(page, page_num + 1, doc_hash, extracted_hashes)
                
                if page_images:
                    all_images[page_num + 1] = page_images
                    logger.info(f"Extracted {len(page_images)} unique images from page {page_num + 1}")
            
            doc.close()
            
            total_images = sum(len(images) for images in all_images.values())
            logger.info(f"Successfully extracted {total_images} unique images from {len(all_images)} pages")
            
        except Exception as e:
            logger.error(f"Failed to extract images from {pdf_path}: {e}")
            raise
        
        return all_images
