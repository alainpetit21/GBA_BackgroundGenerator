"""
Image loading service for the GBA Tile Quantizer.
"""
from __future__ import annotations
from pathlib import Path
from PIL import Image


class ImageLoader:
    """
    Service responsible for loading images from disk.
    """

    def load(self, image_path: str | Path) -> Image.Image:
        """
        Load an image from disk and convert it to RGB.

        Args:
            image_path: Path to the source image.

        Returns:
            A Pillow Image in RGB mode.

        Raises:
            ValueError: If the path is empty.
            FileNotFoundError: If the file does not exist.
            OSError: If Pillow cannot open the file as an image.
        """
        normalized_path = self._normalize_path(image_path)
        self._validate_path_exists(normalized_path)

        with Image.open(normalized_path) as image:
            return image.convert("RGB")

    def _normalize_path(self, image_path: str | Path) -> Path:
        """
        Normalize the provided image path into a Path object.

        Args:
            image_path: Path to normalize.

        Returns:
            A normalized Path object.

        Raises:
            ValueError: If the path is empty.
        """
        if isinstance(image_path, Path):
            normalized_path = image_path
        else:
            stripped_path = image_path.strip()
            if not stripped_path:
                raise ValueError("image_path cannot be empty.")
            normalized_path = Path(stripped_path)

        return normalized_path

    def _validate_path_exists(self, image_path: Path) -> None:
        """
        Validate that the path exists and points to a file.

        Args:
            image_path: Path to validate.

        Raises:
            FileNotFoundError: If the path does not exist or is not a file.
        """
        if not image_path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")

        if not image_path.is_file():
            raise FileNotFoundError(f"Path is not a file: {image_path}")
