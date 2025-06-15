"""Google Colab backend for cloud processing."""

import webbrowser
from pathlib import Path
import json

from ..models.base import StyleTransferModel
from ..utils.logger import get_logger
from ..config import PRESETS_DIR


class ColabBackend:
    """Process videos on Google Colab."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def process_video(self, input_path: Path, output_path: Path,
                     model: StyleTransferModel, fps: int, resize: int,
                     keep_audio: bool = True) -> bool:
        """Process video on Google Colab.
        
        This method creates a custom Colab notebook and opens it in the browser.
        """
        try:
            self.logger.info("☁️  Setting up Google Colab processing")
            
            # Create custom notebook
            notebook_path = self._create_colab_notebook(
                input_path, output_path, model.model_name, fps, resize, keep_audio
            )
            
            # Open in browser
            colab_url = f"https://colab.research.google.com/github/upload"
            self.logger.info(f"Opening Colab notebook: {notebook_path}")
            self.logger.info(f"Please upload the notebook to: {colab_url}")
            
            webbrowser.open(colab_url)
            
            print("\n" + "="*60)
            print("🚀 COLAB PROCESSING SETUP")
            print("="*60)
            print(f"1. Upload this notebook to Colab: {notebook_path}")
            print("2. Upload your input video to Colab's file system")
            print("3. Run all cells in the notebook")
            print("4. Download the styled video from Colab")
            print("="*60)
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Colab setup failed: {e}")
            return False
    
    def _create_colab_notebook(self, input_path: Path, output_path: Path,
                              model_name: str, fps: int, resize: int,
                              keep_audio: bool) -> Path:
        """Create a custom Colab notebook for the processing job."""
        
        # Notebook template
        notebook = {
            "cells": [
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [
                        "# 🎨 Style Transfer Video Processing\n",
                        "\n",
                        f"**Input Video:** `{input_path.name}`\n",
                        f"**Output Video:** `{output_path.name}`\n",
                        f"**Style Model:** `{model_name}`\n",
                        f"**FPS:** {fps}\n",
                        f"**Resize:** {resize}px\n",
                        f"**Keep Audio:** {keep_audio}\n"
                    ]
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [
                        "# Install required packages\n",
                        "!pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118\n",
                        "!pip install opencv-python moviepy pillow tqdm"
                    ]
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [
                        "# Clone the stylize-video repository\n",
                        "!git clone https://github.com/your-repo/stylize-video.git\n",
                        "%cd stylize-video"
                    ]
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [
                        "# Upload your input video\n",
                        "from google.colab import files\n",
                        "import shutil\n",
                        "\n",
                        "print('Please upload your input video:')\n",
                        "uploaded = files.upload()\n",
                        "\n",
                        "# Move uploaded file to expected location\n",
                        f"input_video = '{input_path.name}'\n",
                        "if input_video in uploaded:\n",
                        "    print(f'✅ Video uploaded: {input_video}')\n",
                        "else:\n",
                        "    print('❌ Please upload the correct video file')"
                    ]
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [
                        "# Run style transfer processing\n",
                        f"!python -m stylize_video stylize \\\n",
                        f"  --input {input_path.name} \\\n",
                        f"  --output {output_path.name} \\\n",
                        f"  --model {model_name} \\\n",
                        f"  --backend local \\\n",
                        f"  --fps {fps} \\\n",
                        f"  --resize {resize} \\\n",
                        f"  {'--keep-audio' if keep_audio else '--no-audio'} \\\n",
                        "  --verbose"
                    ]
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [
                        "# Download the result\n",
                        "from google.colab import files\n",
                        "import os\n",
                        "\n",
                        f"if os.path.exists('{output_path.name}'):\n",
                        f"    files.download('{output_path.name}')\n",
                        "    print('✅ Download started!')\n",
                        "else:\n",
                        "    print('❌ Output video not found. Check the processing cell for errors.')"
                    ]
                }
            ],
            "metadata": {
                "kernelspec": {
                    "display_name": "Python 3",
                    "language": "python",
                    "name": "python3"
                },
                "language_info": {
                    "name": "python",
                    "version": "3.10.0"
                }
            },
            "nbformat": 4,
            "nbformat_minor": 0
        }
        
        # Save notebook
        PRESETS_DIR.mkdir(exist_ok=True)
        notebook_path = PRESETS_DIR / f"stylize_{model_name}_{input_path.stem}.ipynb"
        
        with open(notebook_path, 'w') as f:
            json.dump(notebook, f, indent=2)
        
        self.logger.info(f"Created Colab notebook: {notebook_path}")
        return notebook_path
