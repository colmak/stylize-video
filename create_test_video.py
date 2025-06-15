#!/usr/bin/env python3
"""Create a simple test video for style transfer testing."""

import cv2
import numpy as np
from pathlib import Path

def create_test_video():
    """Create a simple test video with moving shapes."""
    output_path = Path("test_video.mp4")
    
    # Video properties
    width, height = 320, 240
    fps = 24
    duration = 3  # seconds
    total_frames = fps * duration
    
    # Create video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
    
    print(f"Creating test video: {output_path}")
    print(f"Resolution: {width}x{height}, FPS: {fps}, Duration: {duration}s")
    
    for frame_idx in range(total_frames):
        # Create a frame with moving shapes
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Background gradient
        for y in range(height):
            frame[y, :, 0] = int(255 * y / height)  # Red gradient
            frame[y, :, 2] = int(255 * (1 - y / height))  # Blue gradient
        
        # Moving circle
        center_x = int(width * 0.3 + 0.4 * width * np.sin(2 * np.pi * frame_idx / total_frames))
        center_y = int(height * 0.5)
        radius = 20
        cv2.circle(frame, (center_x, center_y), radius, (0, 255, 0), -1)
        
        # Moving rectangle
        rect_x = int(width * 0.1 + 0.6 * width * frame_idx / total_frames)
        rect_y = int(height * 0.7)
        cv2.rectangle(frame, (rect_x, rect_y), (rect_x + 30, rect_y + 20), (255, 255, 0), -1)
        
        # Add some text
        cv2.putText(frame, f"Frame {frame_idx}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        out.write(frame)
    
    out.release()
    print(f"✅ Test video created: {output_path}")
    return output_path

if __name__ == "__main__":
    create_test_video()
