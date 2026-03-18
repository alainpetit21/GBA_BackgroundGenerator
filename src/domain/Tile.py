"""
Tile domain model for the GBA Tile Quantizer.
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Tile:
    """
    Represents a single 8x8 indexed tile.

    Each pixel is stored as a palette index in the range 0..15.
    The tile contains exactly 64 pixels in row-major order.
    """

    pixels: tuple[int, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        """
        Validate the tile after initialization.
        """
        self._validate_pixels()

    def _validate_pixels(self) -> None:
        """
        Validate the tile pixel data.

        Raises:
            ValueError: If the tile does not contain exactly 64 pixels
                        or if any palette index is invalid.
        """
        if len(self.pixels) != 64:
            raise ValueError("Tile must contain exactly 64 pixels for an 8x8 tile.")

        for index, value in enumerate(self.pixels):
            if not isinstance(value, int):
                raise ValueError(
                    f"Tile pixel at index {index} must be an integer palette index."
                )

            if value < 0 or value > 15:
                raise ValueError(
                    f"Tile pixel at index {index} must be between 0 and 15."
                )

    @staticmethod
    def from_rows(rows: list[list[int]]) -> "Tile":
        """
        Create a tile from an 8x8 list of rows.

        Args:
            rows: 8 rows containing 8 palette indices each.

        Returns:
            A Tile instance.

        Raises:
            ValueError: If the input is not exactly 8x8 or contains invalid values.
        """
        if len(rows) != 8:
            raise ValueError("Tile rows must contain exactly 8 rows.")

        flattened_pixels: list[int] = []

        for row_index, row in enumerate(rows):
            if len(row) != 8:
                raise ValueError(
                    f"Tile row at index {row_index} must contain exactly 8 pixels."
                )
            flattened_pixels.extend(row)

        return Tile(tuple(flattened_pixels))

    def get_pixel(self, x: int, y: int) -> int:
        """
        Return the palette index at the given coordinates.

        Args:
            x: X coordinate in the range 0..7.
            y: Y coordinate in the range 0..7.

        Returns:
            The palette index at (x, y).

        Raises:
            ValueError: If the coordinates are out of range.
        """
        self._validate_coordinates(x, y)
        return self.pixels[(y * 8) + x]

    def to_rows(self) -> list[list[int]]:
        """
        Return the tile as an 8x8 list of rows.

        Returns:
            The tile pixels arranged as rows.
        """
        return [
            list(self.pixels[row_start:row_start + 8])
            for row_start in range(0, 64, 8)
        ]

    def flipped_horizontal(self) -> "Tile":
        """
        Return a new tile flipped horizontally.

        Returns:
            A horizontally flipped Tile.
        """
        rows = self.to_rows()
        flipped_rows = [list(reversed(row)) for row in rows]
        return Tile.from_rows(flipped_rows)

    def flipped_vertical(self) -> "Tile":
        """
        Return a new tile flipped vertically.

        Returns:
            A vertically flipped Tile.
        """
        rows = self.to_rows()
        flipped_rows = list(reversed(rows))
        return Tile.from_rows(flipped_rows)

    def flipped_horizontal_vertical(self) -> "Tile":
        """
        Return a new tile flipped horizontally and vertically.

        Returns:
            A horizontally and vertically flipped Tile.
        """
        return self.flipped_horizontal().flipped_vertical()

    def to_4bpp_binary(self) -> bytes:
        """
        Encode the tile as GBA 4bpp binary data.

        GBA 4bpp tiles use 32 bytes:
        - 2 pixels per byte
        - low nibble = first pixel
        - high nibble = second pixel

        Returns:
            The 32-byte binary representation of the tile.
        """
        output = bytearray()

        for index in range(0, 64, 2):
            first_pixel = self.pixels[index]
            second_pixel = self.pixels[index + 1]
            packed_byte = first_pixel | (second_pixel << 4)
            output.append(packed_byte)

        return bytes(output)

    def difference_score(self, other: "Tile") -> int:
        """
        Compute a simple per-pixel index difference score.

        This is a basic metric intended for v1 experimentation.
        Lower is better. Zero means exact match.

        Args:
            other: Tile to compare against.

        Returns:
            Sum of absolute palette-index differences.

        Raises:
            TypeError: If other is not a Tile.
        """
        if not isinstance(other, Tile):
            raise TypeError("other must be a Tile instance.")

        score = 0
        for self_pixel, other_pixel in zip(self.pixels, other.pixels):
            score += abs(self_pixel - other_pixel)

        return score

    def exact_match(self, other: "Tile") -> bool:
        """
        Check whether this tile matches another tile exactly.

        Args:
            other: Tile to compare against.

        Returns:
            True if both tiles are identical, otherwise False.
        """
        return self == other

    def unique_palette_indices(self) -> set[int]:
        """
        Return the set of palette indices used by this tile.

        Returns:
            A set of unique palette indices.
        """
        return set(self.pixels)

    def uses_palette_index(self, palette_index: int) -> bool:
        """
        Check whether the tile uses a specific palette index.

        Args:
            palette_index: Palette index to look for.

        Returns:
            True if the tile uses the palette index, otherwise False.

        Raises:
            ValueError: If the palette index is out of range.
        """
        if palette_index < 0 or palette_index > 15:
            raise ValueError("palette_index must be between 0 and 15.")

        return palette_index in self.pixels

    @staticmethod
    def _validate_coordinates(x: int, y: int) -> None:
        """
        Validate tile coordinates.

        Args:
            x: X coordinate.
            y: Y coordinate.

        Raises:
            ValueError: If the coordinates are out of range.
        """
        if x < 0 or x > 7:
            raise ValueError("x must be between 0 and 7.")

        if y < 0 or y > 7:
            raise ValueError("y must be between 0 and 7.")
