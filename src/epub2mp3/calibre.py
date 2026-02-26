"""Calibre conversion utilities."""

from pathlib import Path
from typing import Optional

from .utils import run_command


def convert_epub_to_html(
    epub_path: Path,
    output_html: Path,
    verbose: bool = False
) -> bool:
    """
    Convert an EPUB file to HTML using Calibre's ebook-convert.
    
    Args:
        epub_path: Path to the input EPUB file
        output_html: Path to the output HTML file
        verbose: Print command output
        
    Returns:
        True if conversion succeeded, False otherwise
    """
    # Ensure output directory exists
    output_html.parent.mkdir(parents=True, exist_ok=True)
    
    # Build the ebook-convert command
    cmd = [
        "ebook-convert",
        str(epub_path),
        str(output_html),
        "--enable-heuristics",
    ]
    
    if verbose:
        print(f"Converting {epub_path.name} to HTML...")
    
    returncode, stdout, stderr = run_command(cmd, verbose=verbose)
    
    if returncode != 0:
        print(f"❌ Error converting EPUB to HTML:")
        print(f"  {stderr}")
        return False
    
    if verbose and stdout:
        print(stdout)
    
    if not output_html.exists():
        print(f"❌ Error: Output HTML file was not created: {output_html}")
        return False
    
    if verbose:
        print(f"✓ Converted to HTML: {output_html}")
    
    return True


def extract_metadata(epub_path: Path, verbose: bool = False) -> dict[str, str]:
    """
    Extract metadata from an EPUB file using Calibre.
    
    Args:
        epub_path: Path to the EPUB file
        verbose: Print verbose output
        
    Returns:
        Dictionary with title, author, etc.
    """
    cmd = ["ebook-meta", str(epub_path)]
    
    returncode, stdout, stderr = run_command(cmd, verbose=verbose)
    
    metadata = {
        "title": epub_path.stem,  # Default to filename
        "author": "Unknown",
    }
    
    if returncode == 0 and stdout:
        # Parse the output
        for line in stdout.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()
                
                if key == 'title':
                    metadata['title'] = value
                elif key == 'author(s)':
                    metadata['author'] = value
    
    if verbose:
        print(f"Metadata: {metadata}")
    
    return metadata
