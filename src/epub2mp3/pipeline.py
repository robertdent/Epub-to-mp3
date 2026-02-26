"""Main pipeline for EPUB to MP3 conversion."""

import json
import time
from pathlib import Path
from typing import Optional

from . import calibre, chapters, ffmpeg, ollama_cleaner, piper_tts
from .utils import ensure_dir, format_duration, sanitize_filename


class Pipeline:
    """Main conversion pipeline."""
    
    def __init__(self, epub_path: Path, output_dir: Path, config: dict):
        self.epub_path = epub_path
        self.output_dir = output_dir
        self.config = config
        self.verbose = config.get("verbose", False)
        
        # Extract book metadata
        self.metadata = calibre.extract_metadata(epub_path, verbose=self.verbose)
        
        # Create book-specific output directory
        book_title = sanitize_filename(self.metadata["title"])
        self.book_dir = output_dir / book_title
        
        # Setup directory structure
        self.html_dir = self.book_dir / "html"
        self.text_dir = self.book_dir / "text"
        self.wav_dir = self.book_dir / "wav"
        self.mp3_dir = self.book_dir / "mp3"
        
        ensure_dir(self.html_dir)
        ensure_dir(self.text_dir)
        ensure_dir(self.wav_dir)
        ensure_dir(self.mp3_dir)
        
        self.html_path = self.html_dir / "book.html"
        self.metadata_path = self.book_dir / "metadata.json"
    
    def run(self):
        """Run the complete conversion pipeline."""
        start_time = time.time()
        
        print(f"\n{'='*60}")
        print(f"Converting: {self.metadata['title']}")
        print(f"Author: {self.metadata['author']}")
        print(f"Output: {self.book_dir}")
        print(f"{'='*60}\n")
        
        # Step 1: Convert EPUB to HTML
        print("Step 1: Converting EPUB to HTML...")
        if not self.html_path.exists() or self.config.get("force"):
            if not calibre.convert_epub_to_html(
                self.epub_path,
                self.html_path,
                verbose=self.verbose
            ):
                raise RuntimeError("Failed to convert EPUB to HTML")
        else:
            print(f"  ✓ HTML already exists: {self.html_path}")
        
        # Step 2: Detect and split chapters
        print("\nStep 2: Detecting chapters...")
        chapter_list = chapters.detect_chapters(
            self.html_path,
            chapter_regex=self.config.get("chapter_regex"),
            verbose=self.verbose
        )
        
        print(f"  Found {len(chapter_list)} chapter(s)")
        
        for ch in chapter_list:
            print(f"    {ch.index}. {ch.title} ({len(ch.text)} chars)")
        
        # Dry run mode - just show chapters and exit
        if self.config.get("dry_run"):
            print("\n✓ Dry run complete - no files generated")
            return
        
        # Step 3: Save chapter text files
        print("\nStep 3: Saving chapter text files...")
        chapter_files = chapters.save_chapters(
            chapter_list,
            self.text_dir,
            verbose=self.verbose
        )
        
        # Step 4: Optional Ollama cleanup
        if self.config.get("use_ollama"):
            if ollama_cleaner.check_ollama_available(verbose=self.verbose):
                print("\nStep 4: Cleaning text with Ollama...")
                self._clean_chapters_with_ollama(chapter_files)
            else:
                print("\n⚠ Step 4: Ollama not available, skipping text cleanup")
        else:
            print("\nStep 4: Text cleanup disabled (--use-ollama not specified)")
        
        # Step 5: Generate WAV files with Piper
        print("\nStep 5: Generating speech with Piper TTS...")
        wav_files = self._generate_wav_files(chapter_files)
        
        # Step 6: Convert WAV to MP3
        print("\nStep 6: Converting to MP3...")
        mp3_files = self._convert_to_mp3(wav_files)
        
        # Step 7: Save metadata
        print("\nStep 7: Saving metadata...")
        self._save_metadata(chapter_list, mp3_files)
        
        # Cleanup intermediate files if requested
        if not self.config.get("keep_intermediates"):
            print("\nCleaning up intermediate files...")
            self._cleanup_intermediates()
        
        elapsed = time.time() - start_time
        print(f"\n{'='*60}")
        print(f"✅ Conversion complete in {format_duration(elapsed)}")
        print(f"MP3 files: {self.mp3_dir}")
        print(f"{'='*60}")
    
    def _clean_chapters_with_ollama(self, chapter_files: list[Path]):
        """Clean chapter text files with Ollama."""
        model = self.config.get("ollama_model", "llama2")
        
        for i, text_file in enumerate(chapter_files, 1):
            print(f"  [{i}/{len(chapter_files)}] Cleaning {text_file.name}...")
            
            with open(text_file, 'r', encoding='utf-8') as f:
                original_text = f.read()
            
            cleaned_text = ollama_cleaner.clean_text_with_ollama(
                original_text,
                model=model,
                verbose=self.verbose
            )
            
            if cleaned_text:
                # Save cleaned version
                with open(text_file, 'w', encoding='utf-8') as f:
                    f.write(cleaned_text)
                print(f"    ✓ Cleaned successfully")
            else:
                print(f"    ⚠ Cleanup failed, using original text")
    
    def _generate_wav_files(self, text_files: list[Path]) -> list[Path]:
        """Generate WAV files from text files."""
        wav_files = []
        voice = self.config.get("voice", "en_US-lessac-medium")
        rate = self.config.get("rate")
        speaker = self.config.get("speaker")
        
        for i, text_file in enumerate(text_files, 1):
            wav_file = self.wav_dir / text_file.with_suffix('.wav').name
            
            # Skip if already exists and not force mode
            if wav_file.exists() and not self.config.get("force"):
                print(f"  [{i}/{len(text_files)}] ✓ WAV already exists: {wav_file.name}")
                wav_files.append(wav_file)
                continue
            
            print(f"  [{i}/{len(text_files)}] Generating {wav_file.name}...")
            
            if piper_tts.generate_speech(
                text_file,
                wav_file,
                voice=voice,
                rate=rate,
                speaker=speaker,
                verbose=self.verbose
            ):
                wav_files.append(wav_file)
            else:
                print(f"    ⚠ Failed to generate WAV for {text_file.name}")
        
        return wav_files
    
    def _convert_to_mp3(self, wav_files: list[Path]) -> list[Path]:
        """Convert WAV files to MP3."""
        mp3_files = []
        bitrate = self.config.get("bitrate", "128k")
        
        for i, wav_file in enumerate(wav_files, 1):
            mp3_file = self.mp3_dir / wav_file.with_suffix('.mp3').name
            
            # Skip if already exists and not force mode
            if mp3_file.exists() and not self.config.get("force"):
                print(f"  [{i}/{len(wav_files)}] ✓ MP3 already exists: {mp3_file.name}")
                mp3_files.append(mp3_file)
                continue
            
            print(f"  [{i}/{len(wav_files)}] Converting {mp3_file.name}...")
            
            if ffmpeg.convert_wav_to_mp3(
                wav_file,
                mp3_file,
                bitrate=bitrate,
                verbose=self.verbose
            ):
                mp3_files.append(mp3_file)
            else:
                print(f"    ⚠ Failed to convert {wav_file.name} to MP3")
        
        return mp3_files
    
    def _save_metadata(self, chapter_list: list, mp3_files: list[Path]):
        """Save pipeline metadata to JSON."""
        chapters_metadata = []
        
        for ch, mp3_file in zip(chapter_list, mp3_files):
            duration = ffmpeg.get_audio_duration(mp3_file, verbose=False)
            
            chapters_metadata.append({
                "index": ch.index,
                "title": ch.title,
                "mp3_path": str(mp3_file.relative_to(self.book_dir)),
                "duration_seconds": duration,
                "duration_formatted": format_duration(duration)
            })
        
        metadata = {
            "book_title": self.metadata["title"],
            "author": self.metadata["author"],
            "epub_source": str(self.epub_path),
            "conversion_config": self.config,
            "chapters": chapters_metadata,
            "total_chapters": len(chapter_list),
        }
        
        with open(self.metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"  ✓ Metadata saved to {self.metadata_path}")
    
    def _cleanup_intermediates(self):
        """Remove intermediate files (HTML, WAV)."""
        import shutil
        
        # Remove HTML directory
        if self.html_dir.exists():
            shutil.rmtree(self.html_dir)
            print(f"  ✓ Removed HTML files")
        
        # Remove WAV directory
        if self.wav_dir.exists():
            shutil.rmtree(self.wav_dir)
            print(f"  ✓ Removed WAV files")
        
        # Optionally remove text files too
        # (Keep them by default as they're small and useful)
