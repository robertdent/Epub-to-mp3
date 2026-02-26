"""Utility functions for epub2mp3."""

import re
import subprocess
from pathlib import Path
from typing import Optional


def sanitize_filename(name: str, max_length: int = 100) -> str:
    """
    Sanitize a string to be safe for use as a filename.
    
    Args:
        name: The string to sanitize
        max_length: Maximum length of the resulting filename
        
    Returns:
        A filesystem-safe string
    """
    # Remove or replace unsafe characters
    safe = re.sub(r'[<>:"/\\|?*]', '', name)
    # Replace multiple spaces with single space
    safe = re.sub(r'\s+', ' ', safe)
    # Strip leading/trailing spaces
    safe = safe.strip()
    # Truncate to max length
    if len(safe) > max_length:
        safe = safe[:max_length].rstrip()
    # If empty after sanitization, use a default
    if not safe:
        safe = "untitled"
    return safe


def check_command_exists(command: str) -> bool:
    """
    Check if a command exists in the system PATH.
    
    Args:
        command: The command to check
        
    Returns:
        True if command exists, False otherwise
    """
    try:
        # Use 'where' on Windows, 'which' on Unix
        check_cmd = 'where' if subprocess.os.name == 'nt' else 'which'
        result = subprocess.run(
            [check_cmd, command],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


def run_command(
    cmd: list[str],
    cwd: Optional[Path] = None,
    verbose: bool = False
) -> tuple[int, str, str]:
    """
    Run a command and return its exit code, stdout, and stderr.
    
    Args:
        cmd: Command and arguments as a list
        cwd: Working directory for the command
        verbose: If True, print the command being run
        
    Returns:
        Tuple of (returncode, stdout, stderr)
    """
    if verbose:
        print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out after 5 minutes"
    except Exception as e:
        return -1, "", str(e)


def format_duration(seconds: float) -> str:
    """
    Format a duration in seconds as HH:MM:SS.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"


def ensure_dir(path: Path) -> Path:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        path: Path to the directory
        
    Returns:
        The path (for chaining)
    """
    path.mkdir(parents=True, exist_ok=True)
    return path
