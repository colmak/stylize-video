"""Style transfer models using neural networks."""

import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.transforms as transforms
from torchvision.models import vgg19
from PIL import Image
import requests
from pathlib import Path

from .base import StyleTransferModel
from ..config import SUPPORTED_MODELS, MODELS_DIR


class TransformerNet(nn.Module):
    """Fast neural style transfer network architecture."""
    
    def __init__(self):
        super(TransformerNet, self).__init__()
        # Initial convolution layers
        self.conv1 = ConvLayer(3, 32, kernel_size=9, stride=1)
        self.in1 = nn.InstanceNorm2d(32, affine=True)
        self.conv2 = ConvLayer(32, 64, kernel_size=3, stride=2)
        self.in2 = nn.InstanceNorm2d(64, affine=True)
        self.conv3 = ConvLayer(64, 128, kernel_size=3, stride=2)
        self.in3 = nn.InstanceNorm2d(128, affine=True)
        
        # Residual layers
        self.res1 = ResidualBlock(128)
        self.res2 = ResidualBlock(128)
        self.res3 = ResidualBlock(128)
        self.res4 = ResidualBlock(128)
        self.res5 = ResidualBlock(128)
        
        # Upsampling layers
        self.deconv1 = UpsampleConvLayer(128, 64, kernel_size=3, stride=1, upsample=2)
        self.in4 = nn.InstanceNorm2d(64, affine=True)
        self.deconv2 = UpsampleConvLayer(64, 32, kernel_size=3, stride=1, upsample=2)
        self.in5 = nn.InstanceNorm2d(32, affine=True)
        self.deconv3 = ConvLayer(32, 3, kernel_size=9, stride=1)
        
        # Non-linearities
        self.relu = nn.ReLU()

    def forward(self, X):
        y = self.relu(self.in1(self.conv1(X)))
        y = self.relu(self.in2(self.conv2(y)))
        y = self.relu(self.in3(self.conv3(y)))
        y = self.res1(y)
        y = self.res2(y)
        y = self.res3(y)
        y = self.res4(y)
        y = self.res5(y)
        y = self.relu(self.in4(self.deconv1(y)))
        y = self.relu(self.in5(self.deconv2(y)))
        y = self.deconv3(y)
        return y


class ConvLayer(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size, stride):
        super(ConvLayer, self).__init__()
        reflection_padding = kernel_size // 2
        self.reflection_pad = nn.ReflectionPad2d(reflection_padding)
        self.conv2d = nn.Conv2d(in_channels, out_channels, kernel_size, stride)

    def forward(self, x):
        out = self.reflection_pad(x)
        out = self.conv2d(out)
        return out


class ResidualBlock(nn.Module):
    def __init__(self, channels):
        super(ResidualBlock, self).__init__()
        self.conv1 = ConvLayer(channels, channels, kernel_size=3, stride=1)
        self.in1 = nn.InstanceNorm2d(channels, affine=True)
        self.conv2 = ConvLayer(channels, channels, kernel_size=3, stride=1)
        self.in2 = nn.InstanceNorm2d(channels, affine=True)
        self.relu = nn.ReLU()

    def forward(self, x):
        residual = x
        out = self.relu(self.in1(self.conv1(x)))
        out = self.in2(self.conv2(out))
        out = out + residual
        return out


class UpsampleConvLayer(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size, stride, upsample=None):
        super(UpsampleConvLayer, self).__init__()
        self.upsample = upsample
        reflection_padding = kernel_size // 2
        self.reflection_pad = nn.ReflectionPad2d(reflection_padding)
        self.conv2d = nn.Conv2d(in_channels, out_channels, kernel_size, stride)

    def forward(self, x):
        x_in = x
        if self.upsample:
            x_in = F.interpolate(x_in, mode='nearest', scale_factor=self.upsample)
        out = self.reflection_pad(x_in)
        out = self.conv2d(out)
        return out


class MosaicModel(StyleTransferModel):
    """Fast neural style transfer model."""
    
    def __init__(self, model_name: str):
        super().__init__(model_name)
        self.model_info = SUPPORTED_MODELS[model_name]
        self.model_path = MODELS_DIR / f"{model_name}.pth"
        self.model = None
    
    def load_model(self):
        """Load the style transfer model."""
        # Create the model architecture
        self.model = TransformerNet()
        
        # Download model weights if URL is provided and weights don't exist
        if self.model_info.get("url") and not self.model_path.exists():
            print(f"Downloading {self.model_name} model...")
            self._download_model()
        
        # Load the pre-trained weights if they exist
        if self.model_path.exists():
            try:
                state_dict = torch.load(self.model_path, map_location=self.device)
                self.model.load_state_dict(state_dict)
                print(f"✅ Loaded {self.model_name} model weights")
            except Exception as e:
                print(f"⚠️  Could not load model weights: {e}")
                print("Using randomly initialized weights (artistic effects may vary)")
        else:
            print(f"ℹ️  Using randomly initialized {self.model_name} model (artistic effects may vary)")
        
        self.model.to(self.device)
        self.model.eval()
        self.is_loaded = True
        print(f"✅ {self.model_name} model loaded on {self.device}")
    
    def _download_model(self):
        """Download model weights."""
        url = self.model_info.get("url")
        if not url:
            return
            
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            with open(self.model_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"✅ Downloaded {self.model_name} model to {self.model_path}")
        except Exception as e:
            print(f"⚠️  Could not download model: {e}")
            print("Will use randomly initialized weights")
    
    def preprocess(self, image: Image.Image) -> torch.Tensor:
        """Preprocess image for style transfer."""
        transform = transforms.Compose([
            transforms.Resize((512, 512)),
            transforms.ToTensor(),
        ])
        
        tensor = transform(image).unsqueeze(0)  # Add batch dimension
        return tensor.to(self.device)
    
    def postprocess(self, tensor: torch.Tensor) -> Image.Image:
        """Convert model output tensor back to PIL Image."""
        # Remove batch dimension and move to CPU
        tensor = tensor.squeeze(0).cpu()
        
        # Clamp values to [0, 1] and convert to [0, 255]
        tensor = torch.clamp(tensor, 0, 1)
        tensor = tensor * 255
        
        # Convert to numpy and transpose
        img_array = tensor.numpy().astype('uint8')
        img_array = img_array.transpose(1, 2, 0)  # CHW -> HWC
        
        return Image.fromarray(img_array)
    
    def forward(self, input_tensor: torch.Tensor) -> torch.Tensor:
        """Run forward pass through the model."""
        with torch.no_grad():
            output = self.model(input_tensor)
            # Apply sigmoid to ensure values are in [0, 1] range
            output = torch.sigmoid(output)
            return output
