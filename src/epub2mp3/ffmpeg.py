"""FFmpeg utilities for audio conversion."""

from pathlib import Path

from .utils import run_command


def convert_wav_to_mp3(
    wav_file: Path,
    mp3_file: Path,
    bitrate: str = "128k",
    verbose: bool = False
) -> bool:
    """
    Convert a WAV file to MP3 using ffmpeg.
    
    Args:
        wav_file: Path to the input WAV file
        mp3_file: Path to the output MP3 file
        bitrate: MP3 bitrate (e.g., "96k", "128k", "192k")
        verbose: Print verbose output
        
    Returns:
        True if conversion succeeded, False otherwise
    """
    if not wav_file.exists():
        print(f"⚠ Warning: WAV file not found: {wav_file}")
        return False
    
    mp3_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Build the ffmpeg command
    cmd = [
        "ffmpeg",
        "-i", str(wav_file),
        "-codec:a", "libmp3lame",
        "-b:a", bitrate,
        "-y",  # Overwrite output file if it exists
        str(mp3_file)
    ]
    
    if not verbose:
        # Suppress ffmpeg's verbose output
        cmd.insert(1, "-loglevel")
        cmd.insert(2, "error")
    
    if verbose:
        print(f"Converting {wav_file.name} to MP3...")
        print(f"  Bitrate: {bitrate}")
    
    returncode, stdout, stderr = run_command(cmd, verbose=verbose)
    
    if returncode != 0:
        print(f"❌ Error converting WAV to MP3:")
        print(f"  {stderr}")
        return False
    
    if verbose and stderr:
        print(stderr)
    
    if not mp3_file.exists():
        print(f"❌ Error: Output MP3 file was not created: {mp3_file}")
        return False
    
    if verbose:
        mp3_size = mp3_file.stat().st_size
        print(f"✓ Created MP3: {mp3_file.name} ({mp3_size / 1024 / 1024:.2f} MB)")
    
    return True


def get_audio_duration(audio_file: Path, verbose: bool = False) -> float:
    """
    Get the duration of an audio file in seconds using ffprobe.
    
    Args:
        audio_file: Path to the audio file
        verbose: Print verbose output
        
    Returns:
        Duration in seconds, or 0.0 if unable to determine
    """
    if not audio_file.exists():
        return 0.0
    
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(audio_file)
    ]
    
    returncode, stdout, stderr = run_command(cmd, verbose=False)
    
    if returncode == 0 and stdout.strip():
        try:
            return float(stdout.strip())
        except ValueError:
            pass
    
    return 0.0
