"""CLI interface for the stylize-video tool."""

import click
import sys
from pathlib import Path
from typing import Optional

from . import config
from .utils.logger import setup_logger
from .backends import get_backend
from .models import get_model


@click.command()
@click.option("--input", "-i", required=True, type=click.Path(exists=True),
              help="Input video file path")
@click.option("--output", "-o", required=True, type=click.Path(),
              help="Output video file path")
@click.option("--model", "-m", default=config.DEFAULT_MODEL,
              type=click.Choice(list(config.SUPPORTED_MODELS.keys())),
              help="Style transfer model to use")
@click.option("--backend", "-b", default=config.DEFAULT_BACKEND,
              type=click.Choice(config.SUPPORTED_BACKENDS),
              help="Backend to use for processing")
@click.option("--fps", default=config.DEFAULT_FPS, type=int,
              help="Output video FPS")
@click.option("--resize", default=config.DEFAULT_RESIZE, type=int,
              help="Resize frames to this dimension (square)")
@click.option("--keep-audio/--no-audio", default=True,
              help="Keep original audio in output video")
@click.option("--verbose", "-v", is_flag=True,
              help="Enable verbose logging")
@click.option("--custom-model", type=click.Path(exists=True),
              help="Path to custom model file (.pth)")
def main(input: str, output: str, model: str, backend: str, fps: int,
         resize: int, keep_audio: bool, verbose: bool, custom_model: Optional[str]):
    """
    Apply neural style transfer to videos.
    
    Transform ordinary videos into artistic masterpieces using deep neural networks.
    """
    
    # Setup logging
    logger = setup_logger(verbose=verbose)
    
    # Display header
    click.echo(click.style("🎨 Style Transfer Video Tool", fg="cyan", bold=True))
    click.echo(f"Input: {input}")
    click.echo(f"Output: {output}")
    click.echo(f"Model: {model}")
    click.echo(f"Backend: {backend}")
    click.echo()
    
    try:
        # Validate inputs
        input_path = Path(input)
        output_path = Path(output)
        
        if not input_path.suffix.lower() in config.SUPPORTED_VIDEO_FORMATS:
            raise click.ClickException(f"Unsupported video format: {input_path.suffix}")
        
        # Create output directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Get the appropriate backend
        backend_instance = get_backend(backend)
        
        # Get the model
        if custom_model:
            model_instance = get_model("custom", custom_model)
        else:
            model_instance = get_model(model)
        
        # Process the video
        logger.info(f"Starting style transfer with {model} model on {backend} backend")
        
        result = backend_instance.process_video(
            input_path=input_path,
            output_path=output_path,
            model=model_instance,
            fps=fps,
            resize=resize,
            keep_audio=keep_audio
        )
        
        if result:
            click.echo(click.style("✅ Style transfer completed successfully!", fg="green", bold=True))
            click.echo(f"Output saved to: {output_path}")
        else:
            click.echo(click.style("❌ Style transfer failed!", fg="red", bold=True))
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Error during processing: {str(e)}")
        click.echo(click.style(f"❌ Error: {str(e)}", fg="red"))
        sys.exit(1)


@click.command()
def list_models():
    """List all available style transfer models."""
    click.echo(click.style("Available Models:", fg="cyan", bold=True))
    click.echo()
    
    for model_name, info in config.SUPPORTED_MODELS.items():
        click.echo(f"📦 {click.style(model_name, fg='yellow', bold=True)}")
        click.echo(f"   Style: {info['description']}")
        click.echo(f"   Type: {info['type']}")
        click.echo(f"   Source: {info['source']}")
        click.echo()


@click.command()
def list_backends():
    """List all available processing backends."""
    click.echo(click.style("Available Backends:", fg="cyan", bold=True))
    click.echo()
    
    backends_info = {
        "local": "Run on local machine using PyTorch + FFmpeg",
        "colab": "Run on Google Colab with GPU acceleration",
        "runpod": "Run on cloud GPU container via RunPod",
        "docker": "Run in Docker container (local or remote)"
    }
    
    for backend, description in backends_info.items():
        click.echo(f"🖥️  {click.style(backend, fg='yellow', bold=True)}")
        click.echo(f"   {description}")
        click.echo()


@click.group()
def cli():
    """Style Transfer Video CLI Tool"""
    pass


cli.add_command(main, name="stylize")
cli.add_command(list_models)
cli.add_command(list_backends)


if __name__ == "__main__":
    cli()
