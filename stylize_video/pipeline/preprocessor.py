"""Video preprocessing - extract frames and audio."""

import cv2
import os
from pathlib import Path
from typing import Tuple, List
import moviepy
from tqdm import tqdm

from ..utils.logger import get_logger
from ..config import TEMP_DIR


class VideoPreprocessor:
    """Handles video preprocessing: frame extraction and audio separation."""
    
    def __init__(self, temp_dir: Path = None):
        self.logger = get_logger(__name__)
        self.temp_dir = temp_dir or TEMP_DIR
        self.frames_dir = None
        self.audio_path = None
    
    def extract_frames(self, video_path: Path, resize: int = None) -> Tuple[Path, float, Tuple[int, int]]:
        """Extract frames from video.
        
        Args:
            video_path: Path to input video
            resize: Target size for frames (square)
            
        Returns:
            Tuple of (frames_directory, fps, original_dimensions)
        """
        self.logger.info(f"Extracting frames from {video_path}")
        
        # Create frames directory
        video_name = video_path.stem
        self.frames_dir = self.temp_dir / f"{video_name}_frames"
        self.frames_dir.mkdir(exist_ok=True)
        
        # Open video
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")
        
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        original_dims = (width, height)
        
        self.logger.info(f"Video properties: {frame_count} frames, {fps} FPS, {width}x{height}")
        
        # Extract frames
        frame_paths = []
        frame_idx = 0
        
        with tqdm(total=frame_count, desc="Extracting frames") as pbar:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Resize frame if requested
                if resize:
                    frame = cv2.resize(frame, (resize, resize))
                
                # Save frame
                frame_path = self.frames_dir / f"frame_{frame_idx:06d}.jpg"
                cv2.imwrite(str(frame_path), frame)
                frame_paths.append(frame_path)
                
                frame_idx += 1
                pbar.update(1)
        
        cap.release()
        
        self.logger.info(f"Extracted {len(frame_paths)} frames to {self.frames_dir}")
        return self.frames_dir, fps, original_dims
    
    def extract_audio(self, video_path: Path) -> Path:
        """Extract audio from video.
        
        Args:
            video_path: Path to input video
            
        Returns:
            Path to extracted audio file
        """
        self.logger.info(f"Extracting audio from {video_path}")
        
        video_name = video_path.stem
        self.audio_path = self.temp_dir / f"{video_name}_audio.wav"
        
        try:
            # Load video and extract audio
            video = moviepy.VideoFileClip(str(video_path))
            if video.audio is not None:
                video.audio.write_audiofile(str(self.audio_path), verbose=False, logger=None)
                video.close()
                self.logger.info(f"Audio extracted to {self.audio_path}")
            else:
                self.logger.warning("No audio track found in video")
                self.audio_path = None
        except Exception as e:
            self.logger.error(f"Failed to extract audio: {e}")
            self.audio_path = None
        
        return self.audio_path
    
    def get_frame_paths(self) -> List[Path]:
        """Get sorted list of frame paths."""
        if not self.frames_dir or not self.frames_dir.exists():
            return []
        
        frame_paths = list(self.frames_dir.glob("frame_*.jpg"))
        return sorted(frame_paths)
    
    def cleanup(self):
        """Clean up temporary files."""
        if self.frames_dir and self.frames_dir.exists():
            import shutil
            shutil.rmtree(self.frames_dir)
            self.logger.info(f"Cleaned up frames directory: {self.frames_dir}")
        
        if self.audio_path and self.audio_path.exists():
            self.audio_path.unlink()
            self.logger.info(f"Cleaned up audio file: {self.audio_path}")
