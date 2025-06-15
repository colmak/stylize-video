"""Model loading and management for style transfer."""

from .base import StyleTransferModel
from .mosaic import MosaicModel
from .custom import CustomModel

# Model registry
MODEL_REGISTRY = {
    "mosaic": MosaicModel,
    "candy": MosaicModel,  # Uses same architecture with different weights
    "rain_princess": MosaicModel,
    "udnie": MosaicModel,
    "custom": CustomModel,
}


def get_model(model_name: str, model_path: str = None) -> StyleTransferModel:
    """Get a model instance by name.
    
    Args:
        model_name: Name of the model to load
        model_path: Path to custom model file (for custom models)
    
    Returns:
        StyleTransferModel instance
    """
    if model_name not in MODEL_REGISTRY:
        raise ValueError(f"Unknown model: {model_name}")
    
    model_class = MODEL_REGISTRY[model_name]
    
    if model_name == "custom":
        if not model_path:
            raise ValueError("Custom model requires model_path")
        return model_class(model_path)
    else:
        return model_class(model_name)


__all__ = ["StyleTransferModel", "get_model"]
