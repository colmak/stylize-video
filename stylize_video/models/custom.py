"""Custom model loader for user-provided models."""

import torch
import torch.nn as nn
import torchvision.transforms as transforms
from PIL import Image
from pathlib import Path

from .base import StyleTransferModel


class CustomModel(StyleTransferModel):
    """Custom style transfer model loader."""
    
    def __init__(self, model_path: str):
        super().__init__("custom")
        self.model_path = Path(model_path)
        
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")
    
    def load_model(self):
        """Load a custom PyTorch model."""
        try:
            # Try to load the full model first
            self.model = torch.load(self.model_path, map_location=self.device)
        except Exception:
            # If that fails, try to load as state dict
            # This requires the user to provide a compatible architecture
            raise NotImplementedError(
                "Custom model architecture loading not yet implemented. "
                "Please provide a complete model file (.pth) that can be loaded with torch.load()"
            )
        
        self.model.to(self.device)
        self.model.eval()
        self.is_loaded = True
        print(f"✅ Custom model loaded from {self.model_path}")
    
    def preprocess(self, image: Image.Image) -> torch.Tensor:
        """Default preprocessing for custom models."""
        # This is a generic preprocessing pipeline
        # Users may need to modify this for their specific models
        transform = transforms.Compose([
            transforms.Resize((512, 512)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
        
        tensor = transform(image).unsqueeze(0)
        return tensor
    
    def postprocess(self, tensor: torch.Tensor) -> Image.Image:
        """Default postprocessing for custom models."""
        # Denormalize
        mean = torch.tensor([0.485, 0.456, 0.406]).view(3, 1, 1)
        std = torch.tensor([0.229, 0.224, 0.225]).view(3, 1, 1)
        
        tensor = tensor.squeeze(0)
        tensor = tensor * std + mean
        tensor = tensor.clamp(0, 1)
        
        # Convert to PIL
        transform = transforms.ToPILImage()
        return transform(tensor)
    
    def forward(self, input_tensor: torch.Tensor) -> torch.Tensor:
        """Run forward pass through the custom model."""
        return self.model(input_tensor)
