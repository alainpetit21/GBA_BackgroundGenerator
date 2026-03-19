"""
Image preprocessing service for the GBA Tile Quantizer.
"""
from __future__ import annotations
from PIL import Image

from config.QuantizationConfig import QuantizationConfig


class ImagePreprocessor:
    """
    Service responsible for preparing source images before quantization.
    """

    def preprocess(
        self,
        image: Image.Image,
        config: QuantizationConfig,
    ) -> Image.Image:
        """
        Preprocess an image for tile-based quantization.

        Args:
            image: Source Pillow image.
            config: Quantization configuration.

        Returns:
            A preprocessed RGB Pillow image.

        Raises:
            ValueError: If the image or configuration is invalid.
        """
        if image is None:
            raise ValueError("image cannot be None.")

        config.validate()

        rgb_image = self._ensure_rgb(image)

        if config.pad_to_tile_grid:
            return self._pad_to_tile_grid(
                rgb_image,
                config.tile_width,
                config.tile_height,
            )

        self._validate_tile_alignment(
            rgb_image,
            config.tile_width,
            config.tile_height,
        )
        return rgb_image

    def _ensure_rgb(self, image: Image.Image) -> Image.Image:
        """
        Ensure the image is in RGB mode.

        Args:
            image: Source Pillow image.

        Returns:
            An RGB Pillow image.
        """
        if image.mode == "RGB":
            return image

        return image.convert("RGB")

    def _validate_tile_alignment(
        self,
        image: Image.Image,
        tile_width: int,
        tile_height: int,
    ) -> None:
        """
        Validate that the image dimensions align to the tile grid.

        Args:
            image: Pillow image to validate.
            tile_width: Tile width in pixels.
            tile_height: Tile height in pixels.

        Raises:
            ValueError: If the image is not aligned to the tile grid.
        """
        width, height = image.size

        if width % tile_width != 0:
            raise ValueError(
                f"Image width {width} is not divisible by tile width {tile_width}."
            )

        if height % tile_height != 0:
            raise ValueError(
                f"Image height {height} is not divisible by tile height {tile_height}."
            )

    def _pad_to_tile_grid(
        self,
        image: Image.Image,
        tile_width: int,
        tile_height: int,
    ) -> Image.Image:
        """
        Pad the image to the nearest tile-aligned dimensions.

        Padding is added on the right and bottom edges only.
        New pixels are filled with black.

        Args:
            image: Source Pillow image.
            tile_width: Tile width in pixels.
            tile_height: Tile height in pixels.

        Returns:
            A new padded Pillow image. If no padding is required,
            the original image is returned.
        """
        original_width, original_height = image.size

        padded_width = self._round_up_to_multiple(original_width, tile_width)
        padded_height = self._round_up_to_multiple(original_height, tile_height)

        if padded_width == original_width and padded_height == original_height:
            return image

        padded_image = Image.new("RGB", (padded_width, padded_height), (0, 0, 0))
        padded_image.paste(image, (0, 0))

        return padded_image

    def _round_up_to_multiple(self, value: int, multiple: int) -> int:
        """
        Round a positive integer up to the nearest multiple.

        Args:
            value: Value to round up.
            multiple: Multiple to round to.

        Returns:
            The rounded-up value.

        Raises:
            ValueError: If multiple is invalid.
        """
        if multiple <= 0:
            raise ValueError("multiple must be greater than 0.")

        remainder = value % multiple
        if remainder == 0:
            return value

        return value + (multiple - remainder)
