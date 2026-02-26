"""Piper TTS utilities."""

import subprocess
from pathlib import Path
from typing import Optional

from .utils import run_command


def generate_speech(
    text_file: Path,
    output_wav: Path,
    voice: str = "en_US-lessac-medium",
    rate: Optional[int] = None,
    speaker: Optional[int] = None,
    verbose: bool = False
) -> bool:
    """
    Generate speech from text using Piper TTS.
    
    Args:
        text_file: Path to the input text file
        output_wav: Path to the output WAV file
        voice: Piper voice model name
        rate: Speech rate (optional, if voice supports it)
        speaker: Speaker ID (optional, if voice supports it)
        verbose: Print verbose output
        
    Returns:
        True if generation succeeded, False otherwise
    """
    output_wav.parent.mkdir(parents=True, exist_ok=True)
    
    # Check if text file has content
    if not text_file.exists():
        print(f"⚠ Warning: Text file not found: {text_file}")
        return False
    
    text_size = text_file.stat().st_size
    if text_size < 10:  # Less than 10 bytes
        print(f"⚠ Warning: Text file too small, skipping: {text_file}")
        return False
    
    # Build the piper command
    # Read text from file and pipe to piper
    try:
        with open(text_file, 'r', encoding='utf-8') as f:
            text_content = f.read()
        
        if not text_content.strip():
            print(f"⚠ Warning: Empty text file, skipping: {text_file}")
            return False
        
        # Use piper with stdin
        cmd = ["piper", "--model", voice, "--output_file", str(output_wav)]
        
        if speaker is not None:
            cmd.extend(["--speaker", str(speaker)])
        
        if verbose:
            print(f"Generating speech for {text_file.name}...")
            print(f"  Voice: {voice}")
            if speaker is not None:
                print(f"  Speaker: {speaker}")
        
        # Run piper with text as stdin
        result = subprocess.run(
            cmd,
            input=text_content,
            text=True,
            capture_output=True,
            timeout=600  # 10 minute timeout for long chapters
        )
        
        if result.returncode != 0:
            print(f"❌ Error generating speech:")
            print(f"  {result.stderr}")
            return False
        
        if verbose and result.stdout:
            print(result.stdout)
        
        if not output_wav.exists():
            print(f"❌ Error: Output WAV file was not created: {output_wav}")
            return False
        
        if verbose:
            wav_size = output_wav.stat().st_size
            print(f"✓ Generated WAV: {output_wav.name} ({wav_size / 1024 / 1024:.2f} MB)")
        
        return True
        
    except subprocess.TimeoutExpired:
        print(f"❌ Error: Piper TTS timed out for {text_file.name}")
        return False
    except Exception as e:
        print(f"❌ Error running Piper: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        return False


def check_piper_installed() -> bool:
    """
    Check if Piper TTS is installed and accessible.
    
    Returns:
        True if Piper is available, False otherwise
    """
    try:
        result = subprocess.run(
            ["piper", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (subprocess.SubprocessError, FileNotFoundError):
        return False
