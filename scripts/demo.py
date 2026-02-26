#!/usr/bin/env python3
"""
Demo script to show epub2mp3 functionality.
This script demonstrates the chapter detection without needing actual TTS/audio tools.
"""

from pathlib import Path
import tempfile
from epub2mp3.chapters import detect_chapters, save_chapters

# Create a sample HTML that simulates what Calibre would produce
SAMPLE_BOOK_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>The Adventures of Test Book</title>
    <meta name="author" content="Test Author">
</head>
<body>
    <h1>Prologue</h1>
    <p>This is the beginning of our story. It sets the stage for everything to come.</p>
    <p>The world was not always as it is today...</p>

    <h1>Chapter 1: The Discovery</h1>
    <p>It was a dark and stormy night when Sarah first discovered the ancient manuscript.</p>
    <p>She had been searching through the dusty archives for weeks, looking for any clue 
    about the lost civilization.</p>
    <p>"This is incredible," she whispered to herself, carefully turning the fragile pages.</p>

    <h1>Chapter 2: The Journey Begins</h1>
    <p>The next morning, Sarah packed her bags and prepared for the expedition.</p>
    <p>She knew this journey would change everything. The manuscript contained coordinates
    to a location deep in the Amazon rainforest.</p>
    
    <h1>Chapter 3: Into the Unknown</h1>
    <p>The jungle was dense and unforgiving. Every step was a challenge.</p>
    <p>But Sarah pressed on, driven by curiosity and determination.</p>
    <p>Three days into the trek, she found it - the entrance to an underground temple.</p>

    <h1>Epilogue</h1>
    <p>Sarah returned home a changed person. What she discovered in that temple
    would reshape humanity's understanding of history.</p>
    <p>But that's a story for another time...</p>
</body>
</html>
"""

def main():
    print("=" * 70)
    print("epub2mp3 Demo - Chapter Detection")
    print("=" * 70)
    print()
    
    # Create temporary directory for demo
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Save sample HTML
        html_file = tmpdir / "sample_book.html"
        html_file.write_text(SAMPLE_BOOK_HTML)
        
        print(f"📖 Sample Book: 'The Adventures of Test Book'")
        print(f"   HTML file created: {html_file.name}")
        print()
        
        # Detect chapters
        print("🔍 Detecting chapters...")
        chapters = detect_chapters(html_file, verbose=False)
        
        print(f"   Found {len(chapters)} chapters:")
        print()
        
        for ch in chapters:
            print(f"   {ch.index}. {ch.title}")
            print(f"      Content: {len(ch.text)} characters")
            print(f"      Preview: {ch.text[:80]}...")
            print()
        
        # Save chapter files
        output_dir = tmpdir / "chapters"
        print(f"💾 Saving chapter text files to: {output_dir}")
        files = save_chapters(chapters, output_dir, verbose=False)
        
        print(f"   Created {len(files)} files:")
        for f in files:
            size = f.stat().st_size
            print(f"      ✓ {f.name} ({size} bytes)")
        
        print()
        print("=" * 70)
        print("Demo Complete!")
        print("=" * 70)
        print()
        print("To use epub2mp3 with a real EPUB file:")
        print("  1. Install Calibre, ffmpeg, and Piper TTS")
        print("  2. Run: epub2mp3 convert yourbook.epub")
        print()
        print("For help: epub2mp3 convert --help")
        print()

if __name__ == "__main__":
    main()
