"""Logging configuration and utilities."""

import logging
import sys
from pathlib import Path
from typing import Optional
from colorama import init, Fore, Back, Style

# Initialize colorama for cross-platform colored output
init(autoreset=True)

# Global logger registry
_loggers = {}


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colored output."""
    
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Back.WHITE + Style.BRIGHT,
    }
    
    def format(self, record):
        # Add color to levelname
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{Style.RESET_ALL}"
        
        return super().format(record)


def setup_logger(name: str = "stylize-video", verbose: bool = False, 
                log_file: Optional[Path] = None) -> logging.Logger:
    """Setup and configure logger.
    
    Args:
        name: Logger name
        verbose: Enable debug logging
        log_file: Optional log file path
        
    Returns:
        Configured logger instance
    """
    # Return existing logger if already configured
    if name in _loggers:
        return _loggers[name]
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if verbose else logging.INFO)
    
    console_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    console_formatter = ColoredFormatter(console_format, datefmt="%H:%M:%S")
    console_handler.setFormatter(console_formatter)
    
    logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        file_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        file_formatter = logging.Formatter(file_format, datefmt="%Y-%m-%d %H:%M:%S")
        file_handler.setFormatter(file_formatter)
        
        logger.addHandler(file_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    # Store in registry
    _loggers[name] = logger
    
    return logger


def get_logger(name: str = "stylize-video") -> logging.Logger:
    """Get existing logger or create a basic one.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    if name in _loggers:
        return _loggers[name]
    
    # Create basic logger if not exists
    return setup_logger(name)


class LoggingContext:
    """Context manager for temporary logging configuration."""
    
    def __init__(self, logger: logging.Logger, level: int):
        self.logger = logger
        self.level = level
        self.original_level = None
    
    def __enter__(self):
        self.original_level = self.logger.level
        self.logger.setLevel(self.level)
        return self.logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.setLevel(self.original_level)


def quiet_logger(logger: logging.Logger):
    """Context manager to temporarily quiet a logger."""
    return LoggingContext(logger, logging.ERROR)


def verbose_logger(logger: logging.Logger):
    """Context manager to temporarily make a logger verbose."""
    return LoggingContext(logger, logging.DEBUG)
