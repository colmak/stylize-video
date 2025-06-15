"""Base class for style transfer models."""

from abc import ABC, abstractmethod
import torch
import numpy as np
from PIL import Image
from typing import Union


class StyleTransferModel(ABC):
    """Abstract base class for style transfer models."""
    
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.is_loaded = False
    
    @abstractmethod
    def load_model(self):
        """Load the model weights and prepare for inference."""
        pass
    
    @abstractmethod
    def preprocess(self, image: Image.Image) -> torch.Tensor:
        """Preprocess input image for the model."""
        pass
    
    @abstractmethod
    def postprocess(self, tensor: torch.Tensor) -> Image.Image:
        """Postprocess model output to PIL Image."""
        pass
    
    @abstractmethod
    def forward(self, input_tensor: torch.Tensor) -> torch.Tensor:
        """Run forward pass through the model."""
        pass
    
    def stylize(self, image: Union[Image.Image, np.ndarray]) -> Image.Image:
        """Apply style transfer to an image.
        
        Args:
            image: Input image as PIL Image or numpy array
            
        Returns:
            Stylized PIL Image
        """
        if not self.is_loaded:
            self.load_model()
        
        # Convert numpy array to PIL if needed
        if isinstance(image, np.ndarray):
            image = Image.fromarray(image)
        
        # Preprocess
        input_tensor = self.preprocess(image)
        input_tensor = input_tensor.to(self.device)
        
        # Run inference
        with torch.no_grad():
            output_tensor = self.forward(input_tensor)
        
        # Postprocess
        output_image = self.postprocess(output_tensor)
        
        return output_image
    
    def to(self, device):
        """Move model to specified device."""
        if isinstance(device, str):
            device = torch.device(device)
        self.device = device
        if self.model is not None:
            self.model.to(device)  
        return self
