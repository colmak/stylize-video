#!/usr/bin/env python3
"""
Stylize Video Demo - Showcase of key features

This demo script demonstrates the main capabilities of the stylize-video tool.
"""

import os
import sys
from pathlib import Path

def main():
    """Run the demo."""
    print("🎨 Stylize Video Tool - Demo")
    print("=" * 50)
    
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    print("📋 Available Models:")
    print("-" * 20)
    os.system("python __main__.py list-models")
    
    print("\n🖥️  Available Backends:")
    print("-" * 25)  
    os.system("python __main__.py list-backends")
    
    print("\n📝 CLI Help:")
    print("-" * 15)
    os.system("python __main__.py stylize --help")
    
    print("\n🎬 Example Usage:")
    print("-" * 20)
    print("Create a test video and apply style transfer:")
    print("1. python create_test_video.py")
    print("2. python __main__.py stylize -i test_video.mp4 -o output.mp4 -m mosaic")
    print("3. Open output.mp4 to view the results!")
    
    print("\n✨ Key Features:")
    print("-" * 20)
    print("✅ Multiple neural style transfer models")
    print("✅ GPU acceleration (CUDA) when available")
    print("✅ Multiple backend support (local, colab, runpod, docker)")
    print("✅ Audio preservation")
    print("✅ Customizable output parameters (FPS, resize)")
    print("✅ Progress tracking with rich output")
    print("✅ Robust error handling and fallbacks")
    print("✅ Modular architecture for easy extension")
    
    print("\n🔧 Advanced Usage:")
    print("-" * 20)
    print("# Custom model:")
    print("python __main__.py stylize -i video.mp4 -o output.mp4 --custom-model path/to/model.pth")
    print()
    print("# High resolution with audio:")
    print("python __main__.py stylize -i video.mp4 -o output.mp4 -m candy --resize 512 --keep-audio")
    print()
    print("# Verbose logging:")
    print("python __main__.py stylize -i video.mp4 -o output.mp4 -m rain_princess --verbose")
    
    print("\n🚀 Project Structure:")
    print("-" * 25)
    print("stylize_video/")
    print("├── cli.py          # Command-line interface")
    print("├── config.py       # Configuration settings")
    print("├── models/         # Neural network models")
    print("├── backends/       # Processing backends")
    print("├── pipeline/       # Video processing pipeline")
    print("└── utils/          # Utility functions")
    
    print("\n" + "=" * 50)
    print("🎯 Ready to transform your videos into art!")

if __name__ == "__main__":
    main()
