"""
Palette bank collection domain model for the GBA Tile Quantizer.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from domain.Palette import Palette


@dataclass
class PaletteSet:
    """
    Represents a collection of 4bpp palette banks.
    """

    palettes: list[Palette] = field(default_factory=list)

    def __post_init__(self) -> None:
        self._validate_palettes()

    def _validate_palettes(self) -> None:
        if len(self.palettes) > 16:
            raise ValueError("PaletteSet cannot contain more than 16 palette banks.")

        for index, palette in enumerate(self.palettes):
            if not isinstance(palette, Palette):
                raise ValueError(
                    f"Palette at index {index} is not a Palette instance."
                )

    def palette_count(self) -> int:
        """
        Return the number of palette banks.
        """
        return len(self.palettes)

    def total_color_count(self) -> int:
        """
        Return the total number of used colors across all banks.
        """
        return sum(palette.size() for palette in self.palettes)

    def get_palette(self, index: int) -> Palette:
        """
        Return a palette bank by index.
        """
        return self.palettes[index]

    def is_empty(self) -> bool:
        """
        Check whether the set contains no palette banks.
        """
        return not self.palettes

    def to_binary(self, pad_each_to_16: bool = True) -> bytes:
        """
        Encode all palette banks as concatenated GBA palette data.
        """
        output = bytearray()

        for palette in self.palettes:
            if pad_each_to_16:
                output.extend(palette.padded_to_16_colors().to_binary())
            else:
                output.extend(palette.to_binary())

        return bytes(output)
