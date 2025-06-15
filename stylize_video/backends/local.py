"""Local backend for processing on the current machine."""

import time
from pathlib import Path
from typing import Optional

from ..models.base import StyleTransferModel
from ..pipeline import VideoPreprocessor, StyleProcessor, VideoPostprocessor
from ..utils.logger import get_logger
from ..config import TEMP_DIR


class LocalBackend:
    """Process videos locally using PyTorch and FFmpeg."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def process_video(self, input_path: Path, output_path: Path, 
                     model: StyleTransferModel, fps: int, resize: int,
                     keep_audio: bool = True) -> bool:
        """Process video locally.
        
        Args:
            input_path: Input video path
            output_path: Output video path
            model: Style transfer model
            fps: Target FPS
            resize: Frame resize dimension
            keep_audio: Whether to preserve audio
            
        Returns:
            True if successful
        """
        start_time = time.time()
        
        try:
            self.logger.info("🖥️  Starting local processing")
            
            # Initialize pipeline components
            preprocessor = VideoPreprocessor()
            processor = StyleProcessor(model)
            postprocessor = VideoPostprocessor()
            
            # Step 1: Extract frames and audio
            self.logger.info("📹 Extracting frames...")
            frames_dir, original_fps, original_dims = preprocessor.extract_frames(
                input_path, resize=resize
            )
            
            audio_path = None
            if keep_audio:
                self.logger.info("🔊 Extracting audio...")
                audio_path = preprocessor.extract_audio(input_path)
            
            # Step 2: Process frames
            frame_paths = preprocessor.get_frame_paths()
            if not frame_paths:
                raise ValueError("No frames extracted from video")
            
            styled_frames_dir = TEMP_DIR / f"{input_path.stem}_styled"
            styled_frame_paths = processor.process_frames(frame_paths, styled_frames_dir)
            
            if not styled_frame_paths:
                raise ValueError("No frames were successfully processed")
            
            # Step 3: Create output video
            self.logger.info("🎬 Creating output video...")
            target_fps = fps if fps != original_fps else original_fps
            
            success = postprocessor.create_video(
                styled_frame_paths, output_path, target_fps, audio_path, original_dims
            )
            
            if not success:
                raise ValueError("Failed to create output video")
            
            # Cleanup
            self.logger.info("🧹 Cleaning up temporary files...")
            preprocessor.cleanup()
            if styled_frames_dir.exists():
                import shutil
                shutil.rmtree(styled_frames_dir)
            
            elapsed = time.time() - start_time
            self.logger.info(f"✅ Processing completed in {elapsed:.1f} seconds")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Local processing failed: {e}")
            return False
    
    def test_environment(self) -> bool:
        """Test if the local environment is ready for processing."""
        try:
            import torch
            import cv2
            import moviepy
            
            self.logger.info("✅ All required packages are available")
            
            if torch.cuda.is_available():
                self.logger.info(f"🚀 CUDA available: {torch.cuda.get_device_name()}")
            else:
                self.logger.info("⚠️  CUDA not available, using CPU")
            
            return True
            
        except ImportError as e:
            self.logger.error(f"❌ Missing required package: {e}")
            return False
