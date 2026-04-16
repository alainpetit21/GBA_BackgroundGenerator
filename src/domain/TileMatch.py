"""
Tile match domain model for the GBA Tile Quantizer.
"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class TileMatch:
    """
    Represents the result of matching a tile against another tile.

    This is used for:
    - exact deduplication
    - flip-aware deduplication
    - lossy replacement
    """

    tile_index: int
    horizontal_flip: bool = False
    vertical_flip: bool = False
    score: int = 0
    palette_bank: int | None = None

    def __post_init__(self) -> None:
        """
        Validate the match fields.
        """
        if self.tile_index < 0:
            raise ValueError("tile_index must be greater than or equal to 0.")

        if self.score < 0:
            raise ValueError("score must be greater than or equal to 0.")

        if self.palette_bank is not None and (self.palette_bank < 0 or self.palette_bank > 15):
            raise ValueError("palette_bank must be between 0 and 15 when provided.")
