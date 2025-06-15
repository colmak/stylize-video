"""Backend management for different processing environments."""

from .local import LocalBackend
from .colab import ColabBackend
from .runpod import RunPodBackend
from .docker import DockerBackend

BACKEND_REGISTRY = {
    "local": LocalBackend,
    "colab": ColabBackend,
    "runpod": RunPodBackend,
    "docker": DockerBackend,
}


def get_backend(backend_name: str):
    """Get a backend instance by name."""
    if backend_name not in BACKEND_REGISTRY:
        raise ValueError(f"Unknown backend: {backend_name}")
    
    backend_class = BACKEND_REGISTRY[backend_name]
    return backend_class()


__all__ = ["get_backend", "LocalBackend", "ColabBackend", "RunPodBackend", "DockerBackend"]
