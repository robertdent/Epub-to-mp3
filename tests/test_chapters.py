"""Tests for chapter detection and splitting."""

import pytest
from pathlib import Path
import tempfile

from epub2mp3.chapters import detect_chapters, save_chapters, Chapter


SAMPLE_HTML = """
<!DOCTYPE html>
<html>
<head><title>Test Book</title></head>
<body>
<h1>Chapter 1: The Beginning</h1>
<p>This is the first chapter. It has some text content.</p>
<p>More content in the first chapter.</p>

<h1>Chapter 2: The Middle</h1>
<p>This is the second chapter with different content.</p>
<p>Even more text here.</p>

<h1>Chapter 3: The End</h1>
<p>This is the final chapter.</p>
<p>The conclusion of our story.</p>
</body>
</html>
"""

SAMPLE_HTML_NO_CHAPTERS = """
<!DOCTYPE html>
<html>
<head><title>Test Book</title></head>
<body>
<h1>My Book Title</h1>
<p>This book has no chapter markers.</p>
<p>Just regular content throughout.</p>
</body>
</html>
"""


class TestDetectChapters:
    """Tests for chapter detection."""
    
    def test_detect_standard_chapters(self):
        """Test detection of standard chapter headings."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            f.write(SAMPLE_HTML)
            temp_path = Path(f.name)
        
        try:
            chapters = detect_chapters(temp_path)
            
            assert len(chapters) == 3
            assert chapters[0].title == "Chapter 1: The Beginning"
            assert chapters[1].title == "Chapter 2: The Middle"
            assert chapters[2].title == "Chapter 3: The End"
            
            assert "first chapter" in chapters[0].text
            assert "second chapter" in chapters[1].text
            assert "final chapter" in chapters[2].text
        finally:
            temp_path.unlink()
    
    def test_fallback_single_chapter(self):
        """Test fallback to single chapter when no markers found."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            f.write(SAMPLE_HTML_NO_CHAPTERS)
            temp_path = Path(f.name)
        
        try:
            chapters = detect_chapters(temp_path)
            
            assert len(chapters) == 1
            assert chapters[0].title == "Full Book"
            assert "regular content" in chapters[0].text
        finally:
            temp_path.unlink()
    
    def test_custom_regex(self):
        """Test custom chapter detection regex."""
        html_with_parts = """
        <html><body>
        <h1>Part One</h1>
        <p>Content for part one.</p>
        <h1>Part Two</h1>
        <p>Content for part two.</p>
        </body></html>
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            f.write(html_with_parts)
            temp_path = Path(f.name)
        
        try:
            chapters = detect_chapters(temp_path, chapter_regex=r'Part \w+')
            
            assert len(chapters) == 2
            assert "Part One" in chapters[0].title
            assert "Part Two" in chapters[1].title
        finally:
            temp_path.unlink()


class TestSaveChapters:
    """Tests for saving chapters to files."""
    
    def test_save_chapters(self):
        """Test saving chapters to text files."""
        chapters = [
            Chapter(1, "Chapter One", "Content of chapter one."),
            Chapter(2, "Chapter Two", "Content of chapter two."),
            Chapter(3, "Chapter Three", "Content of chapter three."),
        ]
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            files = save_chapters(chapters, output_dir)
            
            assert len(files) == 3
            
            # Check filenames are zero-padded
            assert files[0].name == "1_Chapter One.txt"
            assert files[1].name == "2_Chapter Two.txt"
            assert files[2].name == "3_Chapter Three.txt"
            
            # Check content
            assert files[0].read_text() == "Content of chapter one."
            assert files[1].read_text() == "Content of chapter two."
            assert files[2].read_text() == "Content of chapter three."
    
    def test_save_chapters_with_padding(self):
        """Test that chapter indices are properly zero-padded."""
        # Create 12 chapters to test 2-digit padding
        chapters = [
            Chapter(i, f"Chapter {i}", f"Content {i}")
            for i in range(1, 13)
        ]
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            files = save_chapters(chapters, output_dir)
            
            assert len(files) == 12
            
            # Check first and last have proper padding
            assert files[0].name.startswith("01_")
            assert files[11].name.startswith("12_")
    
    def test_save_chapters_sanitizes_titles(self):
        """Test that chapter titles are sanitized for filenames."""
        chapters = [
            Chapter(1, "Chapter 1: The Beginning!", "Content"),
            Chapter(2, "Chapter 2: What's Next?", "Content"),
        ]
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            files = save_chapters(chapters, output_dir)
            
            # Check that unsafe characters are removed
            assert "?" not in files[1].name
            assert "!" not in files[0].name
