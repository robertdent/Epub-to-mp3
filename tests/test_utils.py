"""Tests for utility functions."""

import pytest
from pathlib import Path

from epub2mp3.utils import sanitize_filename, format_duration


class TestSanitizeFilename:
    """Tests for filename sanitization."""
    
    def test_basic_sanitization(self):
        """Test basic filename sanitization."""
        assert sanitize_filename("Hello World") == "Hello World"
        assert sanitize_filename("Chapter 1") == "Chapter 1"
    
    def test_remove_unsafe_characters(self):
        """Test removal of unsafe filesystem characters."""
        assert sanitize_filename("Hello/World") == "HelloWorld"
        assert sanitize_filename("Test:File") == "TestFile"
        assert sanitize_filename("File<>Name") == "FileName"
        assert sanitize_filename("File|Name") == "FileName"
        assert sanitize_filename('File"Name') == "FileName"
        assert sanitize_filename("File*Name") == "FileName"
        assert sanitize_filename("File?Name") == "FileName"
    
    def test_multiple_spaces(self):
        """Test that multiple spaces are collapsed."""
        assert sanitize_filename("Hello    World") == "Hello World"
        assert sanitize_filename("Test  File  Name") == "Test File Name"
    
    def test_leading_trailing_spaces(self):
        """Test that leading/trailing spaces are stripped."""
        assert sanitize_filename("  Hello World  ") == "Hello World"
        assert sanitize_filename("\tTest\t") == "Test"
    
    def test_max_length(self):
        """Test that filenames are truncated to max length."""
        long_name = "A" * 200
        result = sanitize_filename(long_name, max_length=50)
        assert len(result) == 50
        assert result == "A" * 50
    
    def test_empty_input(self):
        """Test handling of empty input."""
        assert sanitize_filename("") == "untitled"
        assert sanitize_filename("   ") == "untitled"
        assert sanitize_filename("///") == "untitled"


class TestFormatDuration:
    """Tests for duration formatting."""
    
    def test_seconds_only(self):
        """Test formatting with only seconds."""
        assert format_duration(45) == "00:45"
        assert format_duration(5) == "00:05"
    
    def test_minutes_and_seconds(self):
        """Test formatting with minutes and seconds."""
        assert format_duration(125) == "02:05"
        assert format_duration(3599) == "59:59"
    
    def test_hours_minutes_seconds(self):
        """Test formatting with hours, minutes, and seconds."""
        assert format_duration(3600) == "01:00:00"
        assert format_duration(3665) == "01:01:05"
        assert format_duration(7384) == "02:03:04"
    
    def test_zero_duration(self):
        """Test zero duration."""
        assert format_duration(0) == "00:00"
