"""
Palette domain model for the GBA Tile Quantizer.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Iterable


@dataclass
class Palette:
    """
    Represents a palette of RGB colors used by an indexed image or tileset.

    Colors are stored as (red, green, blue) tuples using 8-bit channel values.
    """

    colors: list[tuple[int, int, int]] = field(default_factory=list)

    def __post_init__(self) -> None:
        """
        Validate the palette after initialization.
        """
        self._validate_colors()

    def _validate_colors(self) -> None:
        """
        Validate all palette colors.

        Raises:
            ValueError: If the palette contains invalid data.
        """
        if len(self.colors) > 16:
            raise ValueError("Palette cannot contain more than 16 colors for 4bpp GBA output.")

        for index, color in enumerate(self.colors):
            if len(color) != 3:
                raise ValueError(f"Color at index {index} must contain exactly 3 components.")

            red, green, blue = color

            if not self._is_valid_channel_value(red):
                raise ValueError(f"Red channel at index {index} must be between 0 and 255.")

            if not self._is_valid_channel_value(green):
                raise ValueError(f"Green channel at index {index} must be between 0 and 255.")

            if not self._is_valid_channel_value(blue):
                raise ValueError(f"Blue channel at index {index} must be between 0 and 255.")

    @staticmethod
    def _is_valid_channel_value(value: int) -> bool:
        """
        Check whether a channel value is a valid 8-bit integer.

        Args:
            value: Channel value to validate.

        Returns:
            True if valid, otherwise False.
        """
        return isinstance(value, int) and 0 <= value <= 255

    def add_color(self, color: tuple[int, int, int]) -> None:
        """
        Add a color to the palette.

        Args:
            color: RGB color tuple.

        Raises:
            ValueError: If adding the color would exceed 16 entries
                        or if the color is invalid.
        """
        if len(self.colors) >= 16:
            raise ValueError("Cannot add more than 16 colors to a 4bpp palette.")

        test_colors = self.colors + [color]
        test_palette = Palette(test_colors)
        self.colors = test_palette.colors

    def extend(self, colors: Iterable[tuple[int, int, int]]) -> None:
        """
        Add multiple colors to the palette.

        Args:
            colors: Iterable of RGB color tuples.

        Raises:
            ValueError: If the resulting palette would be invalid.
        """
        test_colors = self.colors + list(colors)
        test_palette = Palette(test_colors)
        self.colors = test_palette.colors

    def get_color(self, index: int) -> tuple[int, int, int]:
        """
        Return a palette color by index.

        Args:
            index: Palette index.

        Returns:
            The RGB tuple at the given index.

        Raises:
            IndexError: If the index is out of range.
        """
        return self.colors[index]

    def size(self) -> int:
        """
        Return the number of colors in the palette.

        Returns:
            The number of palette entries.
        """
        return len(self.colors)

    def is_empty(self) -> bool:
        """
        Check whether the palette is empty.

        Returns:
            True if the palette contains no colors, otherwise False.
        """
        return len(self.colors) == 0

    def to_gba_color(self, color: tuple[int, int, int]) -> int:
        """
        Convert an 8-bit RGB color to GBA 15-bit BGR format.

        GBA format uses:
        - bits 0-4   = red
        - bits 5-9   = green
        - bits 10-14 = blue
        - bit 15     = unused

        Args:
            color: RGB color tuple.

        Returns:
            The color encoded as a 15-bit GBA integer.
        """
        red, green, blue = color

        gba_red = red >> 3
        gba_green = green >> 3
        gba_blue = blue >> 3

        return gba_red | (gba_green << 5) | (gba_blue << 10)

    def to_gba_color_list(self) -> list[int]:
        """
        Convert the entire palette to a list of GBA 15-bit colors.

        Returns:
            A list of 15-bit GBA color integers.
        """
        return [self.to_gba_color(color) for color in self.colors]

    def to_binary(self) -> bytes:
        """
        Encode the palette as little-endian GBA binary data.

        Each GBA color entry is 2 bytes.

        Returns:
            Palette bytes in little-endian format.
        """
        output = bytearray()

        for gba_color in self.to_gba_color_list():
            output.extend(gba_color.to_bytes(2, byteorder="little", signed=False))

        return bytes(output)

    def padded_to_16_colors(self) -> "Palette":
        """
        Return a new palette padded to exactly 16 colors.

        Missing entries are filled with black.

        Returns:
            A new Palette instance containing exactly 16 colors.
        """
        padded_colors = list(self.colors)

        while len(padded_colors) < 16:
            padded_colors.append((0, 0, 0))

        return Palette(padded_colors)

    def index_of(self, color: tuple[int, int, int]) -> int:
        """
        Return the palette index of a given color.

        Args:
            color: RGB color tuple to find.

        Returns:
            The palette index.

        Raises:
            ValueError: If the color is not present in the palette.
        """
        return self.colors.index(color)
