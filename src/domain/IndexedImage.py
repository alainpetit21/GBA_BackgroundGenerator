"""
IndexedImage domain model for the GBA Tile Quantizer.
"""
from __future__ import annotations
from dataclasses import dataclass

from domain.Palette import Palette


@dataclass
class IndexedImage:
    """
    Represents an image whose pixels are palette indices rather than RGB values.

    Pixels are stored in row-major order.
    """

    width: int
    height: int
    palette: Palette
    pixels: list[int]

    def __post_init__(self) -> None:
        """
        Validate the indexed image after initialization.
        """
        self._validate_dimensions()
        self._validate_pixels()

    def _validate_dimensions(self) -> None:
        """
        Validate the image dimensions.

        Raises:
            ValueError: If width or height is invalid.
        """
        if self.width <= 0:
            raise ValueError("width must be greater than 0.")

        if self.height <= 0:
            raise ValueError("height must be greater than 0.")

    def _validate_pixels(self) -> None:
        """
        Validate the indexed pixel buffer.

        Raises:
            ValueError: If the pixel buffer length is invalid or
                        if a pixel index is out of range.
        """
        expected_pixel_count = self.width * self.height

        if len(self.pixels) != expected_pixel_count:
            raise ValueError(
                f"IndexedImage must contain exactly {expected_pixel_count} pixels, "
                f"but contains {len(self.pixels)}."
            )

        palette_size = self.palette.size()

        for index, pixel_value in enumerate(self.pixels):
            if not isinstance(pixel_value, int):
                raise ValueError(
                    f"Pixel at index {index} must be an integer palette index."
                )

            if pixel_value < 0:
                raise ValueError(
                    f"Pixel at index {index} must be greater than or equal to 0."
                )

            if 0 < palette_size <= pixel_value:
                raise ValueError(
                    f"Pixel at index {index} references palette entry {pixel_value}, "
                    f"but palette size is {palette_size}."
                )

    def get_pixel(self, x: int, y: int) -> int:
        """
        Return the palette index at the given pixel coordinates.

        Args:
            x: X coordinate in pixel space.
            y: Y coordinate in pixel space.

        Returns:
            The palette index at the given coordinates.

        Raises:
            ValueError: If the coordinates are out of range.
        """
        self._validate_coordinates(x, y)
        return self.pixels[self._to_index(x, y)]

    def set_pixel(self, x: int, y: int, palette_index: int) -> None:
        """
        Set the palette index at the given pixel coordinates.

        Args:
            x: X coordinate in pixel space.
            y: Y coordinate in pixel space.
            palette_index: Palette index to assign.

        Raises:
            ValueError: If coordinates or palette index are invalid.
        """
        self._validate_coordinates(x, y)

        if palette_index < 0 or palette_index >= self.palette.size():
            raise ValueError(
                f"palette_index must be between 0 and {self.palette.size() - 1}."
            )

        self.pixels[self._to_index(x, y)] = palette_index

    def get_row(self, y: int) -> list[int]:
        """
        Return a row of indexed pixels.

        Args:
            y: Row index in pixel space.

        Returns:
            A list of palette indices for the requested row.

        Raises:
            ValueError: If y is out of range.
        """
        if y < 0 or y >= self.height:
            raise ValueError(f"y must be between 0 and {self.height - 1}.")

        row_start = y * self.width
        row_end = row_start + self.width
        return self.pixels[row_start:row_end]

    def to_rows(self) -> list[list[int]]:
        """
        Return the indexed image as rows.

        Returns:
            A list of rows of palette indices.
        """
        rows: list[list[int]] = []

        for y in range(self.height):
            rows.append(self.get_row(y))

        return rows

    def is_tile_aligned(self, tile_width: int = 8, tile_height: int = 8) -> bool:
        """
        Check whether the image dimensions align to the tile grid.

        Args:
            tile_width: Tile width in pixels.
            tile_height: Tile height in pixels.

        Returns:
            True if the image dimensions are tile-aligned, otherwise False.

        Raises:
            ValueError: If tile dimensions are invalid.
        """
        if tile_width <= 0:
            raise ValueError("tile_width must be greater than 0.")

        if tile_height <= 0:
            raise ValueError("tile_height must be greater than 0.")

        return (self.width % tile_width == 0) and (self.height % tile_height == 0)

    def tile_width_in_tiles(self, tile_width: int = 8) -> int:
        """
        Return the image width expressed in tiles.

        Args:
            tile_width: Tile width in pixels.

        Returns:
            The number of tiles across.

        Raises:
            ValueError: If the image is not aligned to the tile width.
        """
        if tile_width <= 0:
            raise ValueError("tile_width must be greater than 0.")

        if self.width % tile_width != 0:
            raise ValueError(
                f"Image width {self.width} is not aligned to tile width {tile_width}."
            )

        return self.width // tile_width

    def tile_height_in_tiles(self, tile_height: int = 8) -> int:
        """
        Return the image height expressed in tiles.

        Args:
            tile_height: Tile height in pixels.

        Returns:
            The number of tiles down.

        Raises:
            ValueError: If the image is not aligned to the tile height.
        """
        if tile_height <= 0:
            raise ValueError("tile_height must be greater than 0.")

        if self.height % tile_height != 0:
            raise ValueError(
                f"Image height {self.height} is not aligned to tile height {tile_height}."
            )

        return self.height // tile_height

    def used_palette_indices(self) -> set[int]:
        """
        Return the set of palette indices used by the image.

        Returns:
            A set of used palette indices.
        """
        return set(self.pixels)

    def _to_index(self, x: int, y: int) -> int:
        """
        Convert 2D pixel coordinates into a linear index.

        Args:
            x: X coordinate in pixel space.
            y: Y coordinate in pixel space.

        Returns:
            The linear index.
        """
        return (y * self.width) + x

    def _validate_coordinates(self, x: int, y: int) -> None:
        """
        Validate pixel coordinates.

        Args:
            x: X coordinate in pixel space.
            y: Y coordinate in pixel space.

        Raises:
            ValueError: If the coordinates are out of range.
        """
        if x < 0 or x >= self.width:
            raise ValueError(
                f"x must be between 0 and {self.width - 1}, but got {x}."
            )

        if y < 0 or y >= self.height:
            raise ValueError(
                f"y must be between 0 and {self.height - 1}, but got {y}."
            )
