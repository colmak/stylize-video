"""Core style transfer processing loop."""

import cv2
from pathlib import Path
from typing import List
from PIL import Image
from tqdm import tqdm
import concurrent.futures
import threading

from ..models.base import StyleTransferModel
from ..utils.logger import get_logger


class StyleProcessor:
    """Handles the core style transfer processing loop."""
    
    def __init__(self, model: StyleTransferModel, num_workers: int = 1):
        self.model = model
        self.num_workers = num_workers
        self.logger = get_logger(__name__)
        self._lock = threading.Lock()
    
    def process_frames(self, frame_paths: List[Path], output_dir: Path) -> List[Path]:
        """Apply style transfer to all frames.
        
        Args:
            frame_paths: List of input frame paths
            output_dir: Directory to save styled frames
            
        Returns:
            List of output frame paths
        """
        output_dir.mkdir(exist_ok=True)
        output_paths = []
        
        self.logger.info(f"Processing {len(frame_paths)} frames with {self.model.model_name} model")
        
        if self.num_workers == 1:
            # Single-threaded processing
            output_paths = self._process_frames_sequential(frame_paths, output_dir)
        else:
            # Multi-threaded processing (if model supports it)
            output_paths = self._process_frames_parallel(frame_paths, output_dir)
        
        return sorted(output_paths)
    
    def _process_frames_sequential(self, frame_paths: List[Path], output_dir: Path) -> List[Path]:
        """Process frames sequentially."""
        output_paths = []
        
        with tqdm(frame_paths, desc="Stylizing frames") as pbar:
            for frame_path in pbar:
                output_path = self._process_single_frame(frame_path, output_dir)
                if output_path:
                    output_paths.append(output_path)
                pbar.set_postfix({"current": frame_path.name})
        
        return output_paths
    
    def _process_frames_parallel(self, frame_paths: List[Path], output_dir: Path) -> List[Path]:
        """Process frames in parallel (experimental)."""
        output_paths = []
        
        # Note: Most PyTorch models are not thread-safe, so this is experimental
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            with tqdm(total=len(frame_paths), desc="Stylizing frames") as pbar:
                future_to_path = {
                    executor.submit(self._process_single_frame, path, output_dir): path 
                    for path in frame_paths
                }
                
                for future in concurrent.futures.as_completed(future_to_path):
                    frame_path = future_to_path[future]
                    try:
                        output_path = future.result()
                        if output_path:
                            output_paths.append(output_path)
                    except Exception as e:
                        self.logger.error(f"Error processing {frame_path}: {e}")
                    finally:
                        pbar.update(1)
        
        return output_paths
    
    def _process_single_frame(self, frame_path: Path, output_dir: Path) -> Path:
        """Process a single frame.
        
        Args:
            frame_path: Path to input frame
            output_dir: Directory to save output
            
        Returns:
            Path to output frame
        """
        try:
            # Load frame
            frame = Image.open(frame_path).convert('RGB')
            
            # Apply style transfer (thread-safe model access)
            with self._lock:
                styled_frame = self.model.stylize(frame)
            
            # Save styled frame
            output_path = output_dir / frame_path.name
            styled_frame.save(output_path, quality=95)
            
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error processing frame {frame_path}: {e}")
            return None
    
    def process_single_image(self, image_path: Path, output_path: Path) -> bool:
        """Process a single image (for testing/debugging).
        
        Args:
            image_path: Input image path
            output_path: Output image path
            
        Returns:
            True if successful
        """
        try:
            self.logger.info(f"Processing single image: {image_path}")
            
            # Load and process image
            image = Image.open(image_path).convert('RGB')
            styled_image = self.model.stylize(image)
            
            # Save result
            output_path.parent.mkdir(parents=True, exist_ok=True)
            styled_image.save(output_path, quality=95)
            
            self.logger.info(f"Styled image saved to: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error processing image {image_path}: {e}")
            return False
