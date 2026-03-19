"""
Processing result domain model for the GBA Tile Quantizer.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from domain.IndexedImage import IndexedImage
from domain.Palette import Palette
from domain.TileMap import TileMap
from domain.TileSet import TileSet


@dataclass
class ProcessingResult:
    """
    Represents the final result produced by the processing pipeline.
    """

    indexed_image: IndexedImage
    palette: Palette
    tileset: TileSet
    tilemap: TileMap
    preview_image_bytes: Optional[bytes] = None
    tileset_preview_image_bytes: Optional[bytes] = None

    def unique_tile_count(self) -> int:
        """
        Return the number of unique tiles in the resulting tileset.

        Returns:
            The number of unique tiles.
        """
        return self.tileset.size()

    def palette_color_count(self) -> int:
        """
        Return the number of colors in the resulting palette.

        Returns:
            The number of palette colors.
        """
        return self.palette.size()

    def map_width_in_tiles(self) -> int:
        """
        Return the tilemap width in tiles.

        Returns:
            The tilemap width.
        """
        return self.tilemap.width

    def map_height_in_tiles(self) -> int:
        """
        Return the tilemap height in tiles.

        Returns:
            The tilemap height.
        """
        return self.tilemap.height

    def image_width_in_pixels(self) -> int:
        """
        Return the indexed image width in pixels.

        Returns:
            The image width.
        """
        return self.indexed_image.width

    def image_height_in_pixels(self) -> int:
        """
        Return the indexed image height in pixels.

        Returns:
            The image height.
        """
        return self.indexed_image.height

    def tile_data_size_in_bytes(self) -> int:
        """
        Return the total size of tile data in bytes for 4bpp GBA encoding.

        Each 8x8 4bpp tile occupies 32 bytes.

        Returns:
            The tile data size in bytes.
        """
        return self.tileset.size() * 32

    def palette_data_size_in_bytes(self, padded: bool = False) -> int:
        """
        Return the palette size in bytes.

        Args:
            padded: If True, assume the palette is padded to 16 colors.

        Returns:
            The palette data size in bytes.
        """
        if padded:
            return 16 * 2

        return self.palette.size() * 2

    def used_tile_indices(self) -> set[int]:
        """
        Return the set of tile indices referenced by the tilemap.

        Returns:
            A set of used tile indices.
        """
        return self.tilemap.used_tile_indices()

    def summary(self) -> str:
        """
        Return a human-readable summary of the processing result.

        Returns:
            A summary string.
        """
        return (
            f"Image: {self.image_width_in_pixels()}x{self.image_height_in_pixels()} px, "
            f"Map: {self.map_width_in_tiles()}x{self.map_height_in_tiles()} tiles, "
            f"Palette colors: {self.palette_color_count()}, "
            f"Unique tiles: {self.unique_tile_count()}, "
            f"Tile data: {self.tile_data_size_in_bytes()} bytes"
        )
