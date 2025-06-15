"""I/O utilities and file management."""

import os
import shutil
from pathlib import Path
from typing import Union, List, Optional
import mimetypes

from ..config import SUPPORTED_VIDEO_FORMATS, SUPPORTED_IMAGE_FORMATS
from .logger import get_logger


def ensure_dir(path: Union[str, Path]) -> Path:
    """Ensure directory exists, create if it doesn't.
    
    Args:
        path: Directory path
        
    Returns:
        Path object
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_file_size(path: Union[str, Path]) -> int:
    """Get file size in bytes.
    
    Args:
        path: File path
        
    Returns:
        File size in bytes
    """
    return Path(path).stat().st_size


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def validate_video_file(path: Union[str, Path]) -> bool:
    """Check if file is a valid video file.
    
    Args:
        path: File path
        
    Returns:
        True if valid video file
    """
    path = Path(path)
    
    if not path.exists():
        return False
    
    if not path.is_file():
        return False
    
    # Check extension
    if path.suffix.lower() not in SUPPORTED_VIDEO_FORMATS:
        return False
    
    # Check MIME type
    mime_type, _ = mimetypes.guess_type(str(path))
    if mime_type and not mime_type.startswith('video/'):
        return False
    
    return True


def validate_image_file(path: Union[str, Path]) -> bool:
    """Check if file is a valid image file.
    
    Args:
        path: File path
        
    Returns:
        True if valid image file
    """
    path = Path(path)
    
    if not path.exists():
        return False
    
    if not path.is_file():
        return False
    
    # Check extension
    if path.suffix.lower() not in SUPPORTED_IMAGE_FORMATS:
        return False
    
    return True


def clean_temp_files(temp_dir: Path, pattern: str = "*"):
    """Clean temporary files.
    
    Args:
        temp_dir: Temporary directory
        pattern: File pattern to match (default: all files)
    """
    logger = get_logger(__name__)
    
    if not temp_dir.exists():
        return
    
    try:
        if pattern == "*":
            # Remove entire directory
            shutil.rmtree(temp_dir)
            logger.info(f"Cleaned temp directory: {temp_dir}")
        else:
            # Remove matching files
            for file_path in temp_dir.glob(pattern):
                if file_path.is_file():
                    file_path.unlink()
                elif file_path.is_dir():
                    shutil.rmtree(file_path)
            logger.info(f"Cleaned temp files matching '{pattern}' in {temp_dir}")
    
    except Exception as e:
        logger.warning(f"Failed to clean temp files: {e}")


def copy_with_progress(src: Path, dst: Path, chunk_size: int = 1024*1024) -> bool:
    """Copy file with progress indication.
    
    Args:
        src: Source file
        dst: Destination file
        chunk_size: Copy chunk size in bytes
        
    Returns:
        True if successful
    """
    logger = get_logger(__name__)
    
    try:
        src_size = get_file_size(src)
        dst.parent.mkdir(parents=True, exist_ok=True)
        
        with open(src, 'rb') as f_src, open(dst, 'wb') as f_dst:
            copied = 0
            while True:
                chunk = f_src.read(chunk_size)
                if not chunk:
                    break
                f_dst.write(chunk)
                copied += len(chunk)
                
                # Simple progress indication
                progress = (copied / src_size) * 100
                print(f"\rCopying... {progress:.1f}%", end="", flush=True)
        
        print()  # New line after progress
        logger.info(f"File copied: {src} -> {dst}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to copy file: {e}")
        return False


def find_files(directory: Path, extensions: List[str], recursive: bool = True) -> List[Path]:
    """Find files with specific extensions.
    
    Args:
        directory: Directory to search
        extensions: List of file extensions (with or without dots)
        recursive: Search recursively
        
    Returns:
        List of matching file paths
    """
    # Normalize extensions
    extensions = [ext if ext.startswith('.') else f'.{ext}' for ext in extensions]
    extensions = [ext.lower() for ext in extensions]
    
    files = []
    pattern = "**/*" if recursive else "*"
    
    for file_path in directory.glob(pattern):
        if file_path.is_file() and file_path.suffix.lower() in extensions:
            files.append(file_path)
    
    return sorted(files)


def get_available_filename(path: Path) -> Path:
    """Get available filename by adding suffix if file exists.
    
    Args:
        path: Desired file path
        
    Returns:
        Available file path
    """
    if not path.exists():
        return path
    
    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    counter = 1
    
    while True:
        new_name = f"{stem}_{counter:03d}{suffix}"
        new_path = parent / new_name
        if not new_path.exists():
            return new_path
        counter += 1
