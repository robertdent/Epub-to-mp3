"""Chapter detection and splitting utilities."""

import re
from pathlib import Path
from typing import Optional

from bs4 import BeautifulSoup

from .utils import sanitize_filename


class Chapter:
    """Represents a chapter in the book."""
    
    def __init__(self, index: int, title: str, text: str):
        self.index = index
        self.title = title
        self.text = text
    
    def __repr__(self):
        return f"Chapter({self.index}, '{self.title}', {len(self.text)} chars)"


def detect_chapters(
    html_path: Path,
    chapter_regex: Optional[str] = None,
    verbose: bool = False
) -> list[Chapter]:
    """
    Detect chapters in an HTML file.
    
    Args:
        html_path: Path to the HTML file
        chapter_regex: Custom regex for chapter detection (optional)
        verbose: Print verbose output
        
    Returns:
        List of Chapter objects
    """
    if not html_path.exists():
        raise FileNotFoundError(f"HTML file not found: {html_path}")
    
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'lxml')
    
    # Remove script and style elements
    for element in soup(['script', 'style']):
        element.decompose()
    
    chapters = []
    
    # Strategy 1: Find h1/h2 headings that look like chapters
    if chapter_regex:
        pattern = re.compile(chapter_regex, re.IGNORECASE)
    else:
        # Default pattern: matches "Chapter N", "CHAPTER N", etc.
        pattern = re.compile(r'chapter\s+\d+|prologue|epilogue|introduction', re.IGNORECASE)
    
    headings = soup.find_all(['h1', 'h2'])
    
    if verbose:
        print(f"Found {len(headings)} headings (h1/h2)")
    
    chapter_headings = []
    for heading in headings:
        text = heading.get_text(strip=True)
        if pattern.search(text):
            chapter_headings.append(heading)
            if verbose:
                print(f"  Chapter heading: {text}")
    
    # If we found chapter headings, split by them
    if chapter_headings:
        for i, heading in enumerate(chapter_headings):
            title = heading.get_text(strip=True)
            
            # Collect all text until the next chapter heading
            content = []
            current = heading.next_sibling
            
            # Find the next chapter heading in the DOM
            next_heading = chapter_headings[i + 1] if i + 1 < len(chapter_headings) else None
            
            # Walk through siblings until we hit the next heading
            while current:
                if current == next_heading:
                    break
                
                if hasattr(current, 'get_text'):
                    text = current.get_text(separator=' ', strip=True)
                    if text:
                        content.append(text)
                
                current = current.next_sibling
            
            chapter_text = ' '.join(content)
            
            # Only add if there's actual content
            if chapter_text.strip():
                chapters.append(Chapter(i + 1, title, chapter_text))
    
    # Fallback: If no chapters detected, treat the whole book as one chapter
    if not chapters:
        if verbose:
            print("No chapter headings found, using entire content as single chapter")
        
        body = soup.find('body')
        if body:
            text = body.get_text(separator=' ', strip=True)
            chapters.append(Chapter(1, "Full Book", text))
        else:
            text = soup.get_text(separator=' ', strip=True)
            chapters.append(Chapter(1, "Full Book", text))
    
    if verbose:
        print(f"Detected {len(chapters)} chapter(s)")
    
    return chapters


def save_chapters(
    chapters: list[Chapter],
    output_dir: Path,
    verbose: bool = False
) -> list[Path]:
    """
    Save chapters to individual text files.
    
    Args:
        chapters: List of Chapter objects
        output_dir: Directory to save chapter files
        verbose: Print verbose output
        
    Returns:
        List of created file paths
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Calculate number of digits needed for padding
    num_digits = len(str(len(chapters)))
    
    created_files = []
    
    for chapter in chapters:
        # Create zero-padded filename
        safe_title = sanitize_filename(chapter.title, max_length=50)
        filename = f"{str(chapter.index).zfill(num_digits)}_{safe_title}.txt"
        filepath = output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(chapter.text)
        
        created_files.append(filepath)
        
        if verbose:
            print(f"  Saved: {filename} ({len(chapter.text)} chars)")
    
    return created_files
