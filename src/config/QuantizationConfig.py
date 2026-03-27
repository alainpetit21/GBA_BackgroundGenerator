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

    palette_bank_count: int = 1
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
        if self.palette_bank_count <= 0:
            raise ValueError("palette_bank_count must be greater than 0.")

        if self.palette_bank_count > 16:
            raise ValueError("palette_bank_count must be 16 or less for 4bpp output.")

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
