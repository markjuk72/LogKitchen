"""
Utility helper functions for LogKitchen
"""

import os
from pathlib import Path
from datetime import datetime
from typing import Optional


def ensure_output_dir(directory: str) -> Path:
    """
    Ensure output directory exists

    Args:
        directory: Directory path

    Returns:
        Path object
    """
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_output_filename(log_type: str,
                       output_dir: str = "./output",
                       timestamp: bool = True,
                       extension: str = ".log") -> str:
    """
    Generate output filename

    Args:
        log_type: Type of log (e.g., 'syslog', 'auditd')
        output_dir: Output directory
        timestamp: Include timestamp in filename
        extension: File extension

    Returns:
        Full path to output file
    """
    ensure_output_dir(output_dir)

    if timestamp:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{log_type}_{ts}{extension}"
    else:
        filename = f"{log_type}{extension}"

    return os.path.join(output_dir, filename)


def format_log_count(count: int) -> str:
    """
    Format log count for display

    Args:
        count: Number of logs

    Returns:
        Formatted string
    """
    if count < 1000:
        return str(count)
    elif count < 1000000:
        return f"{count/1000:.1f}K"
    else:
        return f"{count/1000000:.1f}M"


def validate_count(count: str, default: int = 100, max_count: int = 1000000) -> int:
    """
    Validate and parse log count input

    Args:
        count: Count string
        default: Default value
        max_count: Maximum allowed count

    Returns:
        Validated count

    Raises:
        ValueError: If count is invalid
    """
    try:
        num = int(count)
        if num <= 0:
            raise ValueError("Count must be positive")
        if num > max_count:
            raise ValueError(f"Count exceeds maximum of {max_count}")
        return num
    except (ValueError, TypeError):
        return default


def validate_seed(seed: str) -> Optional[int]:
    """
    Validate and parse random seed input

    Args:
        seed: Seed string

    Returns:
        Validated seed or None
    """
    if not seed or seed.lower() in ['none', 'null', 'random']:
        return None

    try:
        return int(seed)
    except ValueError:
        return None
