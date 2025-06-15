"""FFmpeg utilities and video information extraction."""

import subprocess
import json
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import shutil

from .logger import get_logger


def check_ffmpeg() -> bool:
    """Check if FFmpeg is available on the system.
    
    Returns:
        True if FFmpeg is available
    """
    try:
        result = subprocess.run(["ffmpeg", "-version"], 
                              capture_output=True, text=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def check_ffprobe() -> bool:
    """Check if FFprobe is available on the system.
    
    Returns:
        True if FFprobe is available
    """
    try:
        result = subprocess.run(["ffprobe", "-version"], 
                              capture_output=True, text=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def extract_video_info(video_path: Path) -> Optional[Dict[str, Any]]:
    """Extract video information using FFprobe.
    
    Args:
        video_path: Path to video file
        
    Returns:
        Dictionary with video information or None if failed
    """
    logger = get_logger(__name__)
    
    if not check_ffprobe():
        logger.warning("FFprobe not available, cannot extract video info")
        return None
    
    try:
        cmd = [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            str(video_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        info = json.loads(result.stdout)
        
        # Parse and organize the information
        video_info = {
            "format": info.get("format", {}),
            "video_streams": [],
            "audio_streams": [],
            "duration": None,
            "fps": None,
            "resolution": None,
            "has_audio": False,
        }
        
        # Process streams
        for stream in info.get("streams", []):
            if stream.get("codec_type") == "video":
                video_info["video_streams"].append(stream)
                if not video_info["fps"] and "r_frame_rate" in stream:
                    # Parse frame rate
                    fps_str = stream["r_frame_rate"]
                    if "/" in fps_str:
                        num, den = map(int, fps_str.split("/"))
                        video_info["fps"] = num / den if den != 0 else None
                    else:
                        video_info["fps"] = float(fps_str)
                
                if not video_info["resolution"]:
                    width = stream.get("width")
                    height = stream.get("height")
                    if width and height:
                        video_info["resolution"] = (width, height)
            
            elif stream.get("codec_type") == "audio":
                video_info["audio_streams"].append(stream)
                video_info["has_audio"] = True
        
        # Get duration
        format_info = video_info["format"]
        if "duration" in format_info:
            video_info["duration"] = float(format_info["duration"])
        
        return video_info
        
    except (subprocess.CalledProcessError, json.JSONDecodeError, ValueError) as e:
        logger.error(f"Failed to extract video info: {e}")
        return None


def get_video_duration(video_path: Path) -> Optional[float]:
    """Get video duration in seconds.
    
    Args:
        video_path: Path to video file
        
    Returns:
        Duration in seconds or None if failed
    """
    info = extract_video_info(video_path)
    return info.get("duration") if info else None


def get_video_fps(video_path: Path) -> Optional[float]:
    """Get video frame rate.
    
    Args:
        video_path: Path to video file
        
    Returns:
        FPS or None if failed
    """
    info = extract_video_info(video_path)
    return info.get("fps") if info else None


def get_video_resolution(video_path: Path) -> Optional[Tuple[int, int]]:
    """Get video resolution.
    
    Args:
        video_path: Path to video file
        
    Returns:
        Tuple of (width, height) or None if failed
    """
    info = extract_video_info(video_path)
    return info.get("resolution") if info else None


def convert_video_format(input_path: Path, output_path: Path, 
                        codec: str = "libx264", crf: int = 23) -> bool:
    """Convert video format using FFmpeg.
    
    Args:
        input_path: Input video path
        output_path: Output video path
        codec: Video codec to use
        crf: Constant Rate Factor (lower = higher quality)
        
    Returns:
        True if successful
    """
    logger = get_logger(__name__)
    
    if not check_ffmpeg():
        logger.error("FFmpeg not available")
        return False
    
    try:
        cmd = [
            "ffmpeg",
            "-i", str(input_path),
            "-c:v", codec,
            "-crf", str(crf),
            "-c:a", "aac",
            "-y",  # Overwrite output file
            str(output_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        logger.info(f"Video converted: {input_path} -> {output_path}")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg conversion failed: {e.stderr}")
        return False


def extract_frames_ffmpeg(video_path: Path, output_dir: Path, 
                         fps: Optional[float] = None, 
                         start_time: Optional[float] = None,
                         duration: Optional[float] = None) -> bool:
    """Extract frames from video using FFmpeg.
    
    Args:
        video_path: Input video path
        output_dir: Output directory for frames
        fps: Target FPS for extraction (None = all frames)
        start_time: Start time in seconds
        duration: Duration in seconds
        
    Returns:
        True if successful
    """
    logger = get_logger(__name__)
    
    if not check_ffmpeg():
        logger.error("FFmpeg not available")
        return False
    
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        
        cmd = ["ffmpeg", "-i", str(video_path)]
        
        # Add time constraints
        if start_time is not None:
            cmd.extend(["-ss", str(start_time)])
        if duration is not None:
            cmd.extend(["-t", str(duration)])
        
        # Add frame rate filter
        if fps is not None:
            cmd.extend(["-vf", f"fps={fps}"])
        
        # Output pattern
        output_pattern = output_dir / "frame_%06d.jpg"
        cmd.extend(["-y", str(output_pattern)])
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        logger.info(f"Frames extracted to {output_dir}")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg frame extraction failed: {e.stderr}")
        return False


def install_ffmpeg_instructions():
    """Print instructions for installing FFmpeg."""
    print("\n" + "="*50)
    print("📹 FFmpeg Installation Required")
    print("="*50)
    print("FFmpeg is required for video processing.")
    print("\nInstallation instructions:")
    print("\n🐧 Linux (Ubuntu/Debian):")
    print("  sudo apt update && sudo apt install ffmpeg")
    print("\n🍎 macOS:")
    print("  brew install ffmpeg")
    print("\n🪟 Windows:")
    print("  Download from: https://ffmpeg.org/download.html")
    print("  Or use chocolatey: choco install ffmpeg")
    print("\n📦 Conda/Mamba:")
    print("  conda install -c conda-forge ffmpeg")
    print("="*50)
