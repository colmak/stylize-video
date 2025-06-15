"""Video postprocessing - reassemble frames with audio."""

import cv2
from pathlib import Path
from typing import List, Optional, Tuple
import moviepy
from tqdm import tqdm

from ..utils.logger import get_logger


class VideoPostprocessor:
    """Handles video postprocessing: combining frames and audio."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def create_video(self, frame_paths: List[Path], output_path: Path, 
                    fps: float, audio_path: Optional[Path] = None,
                    original_dims: Optional[Tuple[int, int]] = None) -> bool:
        """Create video from styled frames.
        
        Args:
            frame_paths: List of styled frame paths
            output_path: Output video path
            fps: Target FPS
            audio_path: Path to audio file (optional)
            original_dims: Original video dimensions for resizing
            
        Returns:
            True if successful
        """
        if not frame_paths:
            self.logger.error("No frames to process")
            return False
        
        self.logger.info(f"Creating video from {len(frame_paths)} frames")
        
        try:
            # Method 1: Try with moviepy (better quality, audio support)
            success = self._create_video_moviepy(frame_paths, output_path, fps, audio_path, original_dims)
            
            if not success:
                # Method 2: Fallback to OpenCV (no audio)
                self.logger.warning("MoviePy failed, falling back to OpenCV")
                success = self._create_video_opencv(frame_paths, output_path, fps, original_dims)
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error creating video: {e}")
            return False
    
    def _create_video_moviepy(self, frame_paths: List[Path], output_path: Path,
                             fps: float, audio_path: Optional[Path] = None,
                             original_dims: Optional[Tuple[int, int]] = None) -> bool:
        """Create video using MoviePy."""
        try:
            # Create video clip from images
            clip = moviepy.ImageSequenceClip([str(p) for p in frame_paths], fps=fps)
            
            # Resize if needed  
            if original_dims:
                try:
                    clip = clip.resized(original_dims)
                except AttributeError:
                    # Fallback for older MoviePy versions
                    self.logger.warning("MoviePy resize not available, skipping resize")
            
            # Add audio if available
            if audio_path and audio_path.exists():
                self.logger.info("Adding audio track")
                audio = moviepy.AudioFileClip(str(audio_path))
                
                # Match audio duration to video duration
                if audio.duration > clip.duration:
                    audio = audio.subclip(0, clip.duration)
                elif audio.duration < clip.duration:
                    # Loop audio if it's shorter
                    audio = moviepy.afx.audio_loop(audio, duration=clip.duration)
                
                clip = clip.set_audio(audio)
            
            # Write video
            self.logger.info(f"Writing video to {output_path}")
            try:
                clip.write_videofile(
                    str(output_path),
                    fps=fps,
                    codec='libx264',
                    audio_codec='aac' if audio_path else None
                )
            except TypeError:
                # Fallback for different MoviePy versions
                clip.write_videofile(str(output_path), fps=fps)
            
            # Clean up
            clip.close()
            if audio_path:
                audio.close()
            
            self.logger.info("✅ Video created successfully with MoviePy")
            return True
            
        except Exception as e:
            self.logger.error(f"MoviePy video creation failed: {e}")
            return False
    
    def _create_video_opencv(self, frame_paths: List[Path], output_path: Path,
                            fps: float, original_dims: Optional[Tuple[int, int]] = None) -> bool:
        """Create video using OpenCV (no audio support)."""
        try:
            # Get frame dimensions
            first_frame = cv2.imread(str(frame_paths[0]))
            if first_frame is None:
                raise ValueError(f"Cannot read first frame: {frame_paths[0]}")
            
            height, width = first_frame.shape[:2]
            
            # Resize to original dimensions if specified
            if original_dims:
                width, height = original_dims
                first_frame = cv2.resize(first_frame, (width, height))
            
            # Setup video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
            
            if not out.isOpened():
                raise ValueError("Failed to open video writer")
            
            # Write frames
            with tqdm(frame_paths, desc="Writing video") as pbar:
                for frame_path in pbar:
                    frame = cv2.imread(str(frame_path))
                    if frame is None:
                        self.logger.warning(f"Cannot read frame: {frame_path}")
                        continue
                    
                    if original_dims:
                        frame = cv2.resize(frame, (width, height))
                    
                    out.write(frame)
            
            out.release()
            
            self.logger.info("✅ Video created successfully with OpenCV (no audio)")
            return True
            
        except Exception as e:
            self.logger.error(f"OpenCV video creation failed: {e}")
            return False
    
    def add_audio_to_video(self, video_path: Path, audio_path: Path, output_path: Path) -> bool:
        """Add audio to an existing video.
        
        Args:
            video_path: Path to video without audio
            audio_path: Path to audio file
            output_path: Path for output video with audio
            
        Returns:
            True if successful
        """
        try:
            self.logger.info(f"Adding audio from {audio_path} to {video_path}")
            
            video = moviepy.VideoFileClip(str(video_path))
            audio = moviepy.AudioFileClip(str(audio_path))
            
            # Match audio duration to video
            if audio.duration > video.duration:
                audio = audio.subclip(0, video.duration)
            
            final_video = video.set_audio(audio)
            final_video.write_videofile(str(output_path), verbose=False, logger=None)
            
            # Cleanup
            video.close()
            audio.close()
            final_video.close()
            
            self.logger.info("✅ Audio added successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add audio: {e}")
            return False
