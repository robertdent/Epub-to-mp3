# epub2mp3 - EPUB to MP3 Audiobook Converter

Convert EPUB files into chapter-based MP3 audiobooks that work perfectly with Android audiobook players.

## Features

- 📖 **EPUB to MP3**: Complete offline pipeline from EPUB to chapter-based MP3 files
- 🎯 **Smart Chapter Detection**: Automatically detects chapters using headings or custom regex
- 🗣️ **High-Quality TTS**: Uses Piper TTS for natural-sounding speech (CPU-based, no GPU required)
- 🎵 **Optimized Audio**: Configurable MP3 bitrate (default 128k)
- 🤖 **Optional Text Cleanup**: Clean text with Ollama for better TTS output (optional)
- ⚡ **Resume Support**: Skip already-generated files unless `--force` is used
- 📊 **Metadata Output**: JSON metadata with chapter info and durations

## Pipeline

```
EPUB → HTML (Calibre) → Split Chapters → [Optional: Clean with Ollama] → TTS (Piper) → WAV → MP3 (ffmpeg)
```

## Installation

### Prerequisites

1. **Python 3.11+**
   ```bash
   python --version  # Should be 3.11 or higher
   ```

2. **Calibre** (for EPUB conversion)
   - Windows: Download from https://calibre-ebook.com/download_windows
   - Linux: `sudo apt-get install calibre`
   - Verify: `ebook-convert --version`

3. **FFmpeg** (for audio encoding)
   - Windows: Download from https://ffmpeg.org/download.html and add to PATH
   - Linux: `sudo apt-get install ffmpeg`
   - Verify: `ffmpeg -version`

4. **Ollama** (optional, for text cleanup)
   - Download from https://ollama.ai
   - Start Ollama: `ollama serve`
   - Pull a model: `ollama pull llama2`

### Install epub2mp3

1. Clone the repository:
   ```bash
   git clone https://github.com/robertdent/Epub-to-mp3.git
   cd Epub-to-mp3
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install in development mode:
   ```bash
   pip install -e .
   ```

### Download Piper Voice Models

Piper needs voice models to generate speech. Download at least one:

1. Browse available models: https://github.com/rhasspy/piper/blob/master/VOICES.md

2. Download a model (example for English):
   ```bash
   # Create models directory
   mkdir -p ~/.local/share/piper/voices
   
   # Download model (example: en_US-lessac-medium)
   # Download both the .onnx and .onnx.json files
   ```

3. Common voice options:
   - `en_US-lessac-medium` - Good quality, balanced speed
   - `en_US-amy-medium` - Female voice
   - `en_GB-alan-medium` - British accent

## Usage

### Basic Usage

Convert an EPUB to MP3:

```bash
epub2mp3 convert mybook.epub
```

This will create a folder `output/<book-title>/mp3/` with numbered MP3 files.

### With Options

```bash
epub2mp3 convert mybook.epub \
  --out ./audiobooks \
  --voice en_US-lessac-medium \
  --bitrate 96k \
  --verbose
```

### Using Ollama for Text Cleanup

If you have Ollama installed:

```bash
epub2mp3 convert mybook.epub \
  --use-ollama \
  --ollama-model llama2
```

This will clean the text before TTS to:
- Remove page numbers and headers
- Fix OCR errors
- Keep dialogue natural
- Preserve all meaning (no summarization)

### Dry Run (Preview Chapters)

See what chapters would be detected without processing:

```bash
epub2mp3 convert mybook.epub --dry-run
```

### All Options

```
Options:
  --out PATH              Output directory (default: ./output)
  --voice TEXT           Piper voice model (default: en_US-lessac-medium)
  --use-ollama           Use Ollama to clean text before TTS
  --ollama-model TEXT    Ollama model name (default: llama2)
  --keep-intermediates   Keep intermediate files (HTML, WAV, txt)
  --chapter-regex TEXT   Custom regex pattern for chapter detection
  --bitrate TEXT         MP3 bitrate (default: 128k)
  --rate INTEGER         Speech rate (if voice supports it)
  --speaker INTEGER      Speaker ID (if voice supports it)
  --dry-run              Show detected chapters without processing
  --force                Force regeneration of existing MP3 files
  -v, --verbose          Enable verbose output
```

## Output Structure

```
output/
└── Book-Title/
    ├── mp3/
    │   ├── 01_Chapter One.mp3
    │   ├── 02_Chapter Two.mp3
    │   └── 03_Chapter Three.mp3
    ├── text/
    │   ├── 01_Chapter One.txt
    │   ├── 02_Chapter Two.txt
    │   └── 03_Chapter Three.txt
    └── metadata.json
```

The `metadata.json` file contains:
- Book title and author
- List of chapters with titles, durations, and file paths
- Pipeline configuration used

## Examples

### Convert with custom voice and bitrate
```bash
epub2mp3 convert book.epub --voice en_GB-alan-medium --bitrate 96k
```

### Convert with Ollama cleanup and keep intermediate files
```bash
epub2mp3 convert book.epub --use-ollama --keep-intermediates --verbose
```

### Convert with custom chapter detection
```bash
epub2mp3 convert book.epub --chapter-regex "Part \d+|Section \d+"
```

### Force regeneration of all files
```bash
epub2mp3 convert book.epub --force
```

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest

# Run tests
pytest tests/

# Run with coverage
pytest tests/ --cov=epub2mp3
```

### Project Structure

```
epub2mp3/
├── src/epub2mp3/
│   ├── __init__.py
│   ├── cli.py              # CLI interface with Typer
│   ├── pipeline.py         # Main conversion pipeline
│   ├── calibre.py          # EPUB to HTML conversion
│   ├── chapters.py         # Chapter detection and splitting
│   ├── ollama_cleaner.py   # Optional text cleanup
│   ├── piper_tts.py        # Piper TTS integration
│   ├── ffmpeg.py           # WAV to MP3 conversion
│   └── utils.py            # Common utilities
├── tests/
│   ├── test_utils.py
│   └── test_chapters.py
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Troubleshooting

### "ebook-convert not found"
- Ensure Calibre is installed and in your PATH
- Windows: Add Calibre to PATH (usually `C:\Program Files\Calibre2\`)
- Verify: `ebook-convert --version`

### "ffmpeg not found"
- Ensure FFmpeg is installed and in your PATH
- Verify: `ffmpeg -version`

### Piper TTS Issues
- Make sure you have downloaded voice models
- Try a different voice model
- Check Piper logs with `--verbose`

### Ollama not working
- Ensure Ollama is running: `ollama serve`
- Check if model is installed: `ollama list`
- Pull model if needed: `ollama pull llama2`
- The tool will continue without Ollama if it's not available

### Empty or missing chapters
- Try `--dry-run` to see detected chapters
- Use `--chapter-regex` to customize chapter detection
- Add `--verbose` to see detailed logs

## Future Plans

- Web interface for uploading EPUBs
- Mobile app (Expo) for managing conversions
- Support for more TTS engines
- Custom voice training
- Batch conversion

## License

MIT License - See LICENSE file for details

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.
