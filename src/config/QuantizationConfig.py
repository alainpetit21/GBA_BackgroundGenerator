"""
Configuration for image color quantization and tile alignment.
"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class QuantizationConfig:
    """
    Configuration used during image preprocessing and color quantization.
    """

    max_colors: int = 16
    dithering_enabled: bool = False
    quantization_method: str = "median_cut"
    tile_width: int = 8
    tile_height: int = 8
    pad_to_tile_grid: bool = True

    def validate(self) -> None:
        """
        Validate the configuration values.

        Raises:
            ValueError: If one or more configuration values are invalid.
        """
        if self.max_colors <= 0:
            raise ValueError("max_colors must be greater than 0.")

        if self.max_colors > 16:
            raise ValueError("max_colors must be 16 or less for 4bpp output.")

        if self.tile_width != 8:
            raise ValueError("tile_width must be 8 in v1.")

        if self.tile_height != 8:
            raise ValueError("tile_height must be 8 in v1.")

        valid_methods = {"median_cut", "fast_octree"}
        if self.quantization_method not in valid_methods:
            raise ValueError(
                "quantization_method must be one of: "
                f"{', '.join(sorted(valid_methods))}."
            )
