"""Command-line interface for epub2mp3."""

import sys
from pathlib import Path
from typing import Optional

import typer
from typing_extensions import Annotated

from .utils import check_command_exists
from .pipeline import Pipeline

app = typer.Typer(help="Convert EPUB files to chapter-based MP3 audiobooks")


def check_dependencies(use_ollama: bool = False, verbose: bool = False) -> bool:
    """
    Check if required external dependencies are installed.
    
    Args:
        use_ollama: Whether Ollama is required
        verbose: Print additional information
        
    Returns:
        True if all dependencies are available, False otherwise
    """
    missing = []
    
    # Required dependencies
    if not check_command_exists("ebook-convert"):
        missing.append("Calibre (ebook-convert)")
    
    if not check_command_exists("ffmpeg"):
        missing.append("ffmpeg")
    
    # Piper is installed via pip, check for it
    try:
        import piper
        if verbose:
            print("✓ Piper TTS found")
    except ImportError:
        missing.append("piper-tts (pip install piper-tts)")
    
    # Optional dependency
    if use_ollama and not check_command_exists("ollama"):
        typer.echo(
            "⚠ Warning: Ollama not found but --use-ollama was specified. "
            "Text cleaning will be skipped.",
            err=True
        )
    
    if missing:
        typer.echo("❌ Missing required dependencies:", err=True)
        for dep in missing:
            typer.echo(f"  - {dep}", err=True)
        typer.echo(
            "\nPlease install the missing dependencies and try again.",
            err=True
        )
        return False
    
    if verbose:
        typer.echo("✓ All required dependencies found")
    
    return True


@app.command()
def convert(
    epub_path: Annotated[Path, typer.Argument(help="Path to the EPUB file")],
    out: Annotated[Optional[Path], typer.Option(help="Output directory")] = None,
    voice: Annotated[
        str,
        typer.Option(help="Piper voice model to use")
    ] = "en_US-lessac-medium",
    use_ollama: Annotated[
        bool,
        typer.Option(help="Use Ollama to clean text before TTS")
    ] = False,
    ollama_model: Annotated[
        str,
        typer.Option(help="Ollama model name")
    ] = "llama2",
    keep_intermediates: Annotated[
        bool,
        typer.Option(help="Keep intermediate files (HTML, WAV, txt)")
    ] = False,
    chapter_regex: Annotated[
        Optional[str],
        typer.Option(help="Custom regex pattern for chapter detection")
    ] = None,
    bitrate: Annotated[
        str,
        typer.Option(help="MP3 bitrate (e.g., 96k, 128k)")
    ] = "128k",
    rate: Annotated[
        Optional[int],
        typer.Option(help="Speech rate (if voice supports it)")
    ] = None,
    speaker: Annotated[
        Optional[int],
        typer.Option(help="Speaker ID (if voice supports it)")
    ] = None,
    dry_run: Annotated[
        bool,
        typer.Option(help="Show detected chapters without processing")
    ] = False,
    force: Annotated[
        bool,
        typer.Option(help="Force regeneration of existing MP3 files")
    ] = False,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Enable verbose output")
    ] = False,
):
    """
    Convert an EPUB file to chapter-based MP3 audiobooks.
    
    Example:
        epub2mp3 convert mybook.epub --out ./audiobooks --voice en_US-lessac-medium
    """
    # Validate input file
    if not epub_path.exists():
        typer.echo(f"❌ Error: File not found: {epub_path}", err=True)
        raise typer.Exit(1)
    
    if not epub_path.suffix.lower() == ".epub":
        typer.echo(
            f"❌ Error: Input file must be an EPUB file, got: {epub_path.suffix}",
            err=True
        )
        raise typer.Exit(1)
    
    # Check dependencies
    if not check_dependencies(use_ollama=use_ollama, verbose=verbose):
        raise typer.Exit(1)
    
    # Set default output directory
    if out is None:
        out = Path("output")
    
    # Create pipeline configuration
    config = {
        "voice": voice,
        "use_ollama": use_ollama,
        "ollama_model": ollama_model,
        "keep_intermediates": keep_intermediates,
        "chapter_regex": chapter_regex,
        "bitrate": bitrate,
        "rate": rate,
        "speaker": speaker,
        "dry_run": dry_run,
        "force": force,
        "verbose": verbose,
    }
    
    # Run the pipeline
    try:
        pipeline = Pipeline(epub_path, out, config)
        pipeline.run()
        
        typer.echo("\n✅ Conversion complete!")
        
    except KeyboardInterrupt:
        typer.echo("\n\n⚠ Conversion interrupted by user", err=True)
        raise typer.Exit(130)
    except Exception as e:
        typer.echo(f"\n❌ Error during conversion: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        raise typer.Exit(1)


@app.command()
def version():
    """Show version information."""
    from . import __version__
    typer.echo(f"epub2mp3 version {__version__}")


if __name__ == "__main__":
    app()
