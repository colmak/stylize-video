"""Docker backend for containerized processing."""

import subprocess
import shutil
from pathlib import Path
from typing import Optional

from ..models.base import StyleTransferModel
from ..utils.logger import get_logger


class DockerBackend:
    """Process videos in Docker containers."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def process_video(self, input_path: Path, output_path: Path,
                     model: StyleTransferModel, fps: int, resize: int,
                     keep_audio: bool = True) -> bool:
        """Process video in Docker container."""
        try:
            # Check if Docker is available
            if not self._check_docker():
                return False
            
            self.logger.info("🐳 Starting Docker processing")
            
            # Create Dockerfile if it doesn't exist
            dockerfile_path = self._create_dockerfile()
            
            # Build Docker image
            if not self._build_docker_image():
                return False
            
            # Run processing in container
            return self._run_docker_container(input_path, output_path, model.model_name, fps, resize, keep_audio)
            
        except Exception as e:
            self.logger.error(f"❌ Docker processing failed: {e}")
            return False
    
    def _check_docker(self) -> bool:
        """Check if Docker is available."""
        try:
            result = subprocess.run(["docker", "--version"], 
                                  capture_output=True, text=True, check=True)
            self.logger.info(f"✅ Docker available: {result.stdout.strip()}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.logger.error("❌ Docker not found. Please install Docker first.")
            print("\nTo install Docker:")
            print("Ubuntu/Debian: curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh")
            print("Or visit: https://docs.docker.com/get-docker/")
            return False
    
    def _create_dockerfile(self) -> Path:
        """Create Dockerfile for the processing environment."""
        
        dockerfile_content = """# Style Transfer Video Docker Image
FROM pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    ffmpeg \\
    libsm6 \\
    libxext6 \\
    libxrender-dev \\
    libglib2.0-0 \\
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY stylize_video/ ./stylize_video/
COPY __main__.py .

# Create entrypoint script
RUN echo '#!/bin/bash\\n\\
exec python -m stylize_video "$@"' > /app/entrypoint.sh && \\
    chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
"""
        
        dockerfile_path = Path("Dockerfile")
        with open(dockerfile_path, 'w') as f:
            f.write(dockerfile_content)
        
        self.logger.info(f"Created Dockerfile: {dockerfile_path}")
        return dockerfile_path
    
    def _build_docker_image(self) -> bool:
        """Build the Docker image."""
        try:
            self.logger.info("🔨 Building Docker image...")
            
            result = subprocess.run([
                "docker", "build", "-t", "stylize-video", "."
            ], check=True, capture_output=True, text=True)
            
            self.logger.info("✅ Docker image built successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"❌ Docker build failed: {e.stderr}")
            return False
    
    def _run_docker_container(self, input_path: Path, output_path: Path,
                            model_name: str, fps: int, resize: int, keep_audio: bool) -> bool:
        """Run processing in Docker container."""
        try:
            # Prepare paths
            input_abs = input_path.resolve()
            output_abs = output_path.resolve()
            output_abs.parent.mkdir(parents=True, exist_ok=True)
            
            # Docker run command
            docker_cmd = [
                "docker", "run", "--rm",
                "--gpus", "all",  # Enable GPU support if available
                "-v", f"{input_abs.parent}:/input",
                "-v", f"{output_abs.parent}:/output",
                "stylize-video",
                "stylize",
                "--input", f"/input/{input_abs.name}",
                "--output", f"/output/{output_abs.name}",
                "--model", model_name,
                "--backend", "local",
                "--fps", str(fps),
                "--resize", str(resize),
                "--keep-audio" if keep_audio else "--no-audio",
                "--verbose"
            ]
            
            self.logger.info("🚀 Running Docker container...")
            self.logger.debug(f"Docker command: {' '.join(docker_cmd)}")
            
            result = subprocess.run(docker_cmd, check=True)
            
            if output_abs.exists():
                self.logger.info("✅ Docker processing completed successfully")
                return True
            else:
                self.logger.error("❌ Output file not found after Docker processing")
                return False
                
        except subprocess.CalledProcessError as e:
            self.logger.error(f"❌ Docker container execution failed: {e}")
            return False
    
    def cleanup_docker_resources(self):
        """Clean up Docker images and containers."""
        try:
            # Remove containers
            subprocess.run(["docker", "container", "prune", "-f"], 
                         capture_output=True, check=False)
            
            # Optionally remove image
            subprocess.run(["docker", "rmi", "stylize-video"], 
                         capture_output=True, check=False)
            
            self.logger.info("🧹 Docker resources cleaned up")
            
        except Exception as e:
            self.logger.warning(f"Docker cleanup warning: {e}")
