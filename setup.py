"""Setup script for stylize-video package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_path = Path(__file__).parent / "readme.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
if requirements_path.exists():
    requirements = requirements_path.read_text().strip().split('\n')
    requirements = [req.strip() for req in requirements if req.strip() and not req.startswith('#')]
else:
    requirements = [
        "torch>=2.0.0",
        "torchvision>=0.15.0", 
        "opencv-python>=4.8.0",
        "numpy>=1.24.0",
        "Pillow>=10.0.0",
        "click>=8.1.0",
        "tqdm>=4.65.0",
        "moviepy>=1.0.3",
        "requests>=2.31.0",
        "colorama>=0.4.6"
    ]

setup(
    name="stylize-video",
    version="0.1.0",
    author="Style Transfer Video Team",
    author_email="contact@stylize-video.com",
    description="Apply neural style transfer to videos using deep learning",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/stylize-video",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Video",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
        "gpu": [
            "torch>=2.0.0+cu118",
            "torchvision>=0.15.0+cu118",
        ],
    },
    entry_points={
        "console_scripts": [
            "stylize-video=stylize_video.cli:cli",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="video, style-transfer, neural-networks, deep-learning, pytorch, cli",
)
