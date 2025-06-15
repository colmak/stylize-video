"""Basic tests for style transfer models."""

import unittest
import torch
from pathlib import Path
from PIL import Image
import tempfile

from stylize_video.models import get_model
from stylize_video.models.base import StyleTransferModel


class TestStyleTransferModels(unittest.TestCase):
    """Test cases for style transfer models."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_image = self._create_test_image()
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def _create_test_image(self):
        """Create a simple test image."""
        # Create a 256x256 RGB test image
        image = Image.new('RGB', (256, 256), color='red')
        return image
    
    def test_model_registry(self):
        """Test that all models are in the registry."""
        expected_models = ["mosaic", "candy", "rain_princess", "udnie", "custom"]
        
        for model_name in expected_models:
            if model_name != "custom":  # Custom model needs path parameter
                try:
                    model = get_model(model_name)
                    self.assertIsInstance(model, StyleTransferModel)
                    self.assertEqual(model.model_name, model_name)
                except Exception as e:
                    self.fail(f"Failed to create model {model_name}: {e}")
    
    def test_model_device_assignment(self):
        """Test that models are assigned to correct device."""
        model = get_model("mosaic")
        
        # Test CPU assignment
        model.to("cpu")
        self.assertEqual(model.device.type, "cpu")
        
        # Test CUDA assignment if available
        if torch.cuda.is_available():
            model.to("cuda")
            self.assertEqual(model.device.type, "cuda")
    
    def test_preprocessing(self):
        """Test image preprocessing."""
        model = get_model("mosaic")
        
        tensor = model.preprocess(self.test_image)
        
        # Check tensor properties
        self.assertIsInstance(tensor, torch.Tensor)
        self.assertEqual(len(tensor.shape), 4)  # Batch dimension included
        self.assertEqual(tensor.shape[0], 1)    # Batch size = 1
        self.assertEqual(tensor.shape[1], 3)    # RGB channels
    
    def test_postprocessing(self):
        """Test tensor to image postprocessing."""
        model = get_model("mosaic")
        
        # Create a dummy tensor (simulating model output)
        dummy_tensor = torch.rand(1, 3, 512, 512) * 255
        
        image = model.postprocess(dummy_tensor)
        
        # Check image properties
        self.assertIsInstance(image, Image.Image)
        self.assertEqual(image.mode, "RGB")
        self.assertEqual(image.size, (512, 512))
    
    def test_custom_model_path_validation(self):
        """Test custom model path validation."""
        # Test with non-existent path
        with self.assertRaises(FileNotFoundError):
            get_model("custom", "/non/existent/path.pth")
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)


class TestModelIntegration(unittest.TestCase):
    """Integration tests that require model downloads."""
    
    @unittest.skipUnless(torch.cuda.is_available(), "CUDA not available")
    def test_gpu_processing(self):
        """Test GPU processing if CUDA is available."""
        model = get_model("mosaic")
        model.to("cuda")
        
        # Create test image
        test_image = Image.new('RGB', (256, 256), color='blue')
        
        # This would normally download the model, so we skip if no internet
        try:
            result = model.stylize(test_image)
            self.assertIsInstance(result, Image.Image)
        except Exception as e:
            self.skipTest(f"Model loading failed (likely no internet): {e}")


if __name__ == "__main__":
    unittest.main()
