"""
Tile map building service for the GBA Tile Quantizer.
"""
from __future__ import annotations

from domain.TileMap import TileMap, TileMapEntry


class TileMapBuilder:
    """
    Service responsible for constructing TileMap instances.
    """

    def build_from_tile_indices(
        self,
        width: int,
        height: int,
        tile_indices: list[int],
    ) -> TileMap:
        """
        Build a TileMap from a flat list of tile indices.

        Args:
            width: Tile map width in tiles.
            height: Tile map height in tiles.
            tile_indices: Flat list of tile indices in row-major order.

        Returns:
            A TileMap instance.

        Raises:
            ValueError: If dimensions or tile index count are invalid.
        """
        self._validate_dimensions(width, height)

        expected_count = width * height
        if len(tile_indices) != expected_count:
            raise ValueError(
                f"tile_indices must contain exactly {expected_count} values, "
                f"but contains {len(tile_indices)}."
            )

        entries = [
            TileMapEntry(tile_index=tile_index)
            for tile_index in tile_indices
        ]

        return TileMap(
            width=width,
            height=height,
            entries=entries,
        )

    def build_from_entries(
        self,
        width: int,
        height: int,
        entries: list[TileMapEntry],
    ) -> TileMap:
        """
        Build a TileMap from a flat list of TileMapEntry values.

        Args:
            width: Tile map width in tiles.
            height: Tile map height in tiles.
            entries: Flat list of tile map entries in row-major order.

        Returns:
            A TileMap instance.

        Raises:
            ValueError: If dimensions or entry count are invalid.
            TypeError: If any entry is not a TileMapEntry.
        """
        self._validate_dimensions(width, height)

        expected_count = width * height
        if len(entries) != expected_count:
            raise ValueError(
                f"entries must contain exactly {expected_count} values, "
                f"but contains {len(entries)}."
            )

        for index, entry in enumerate(entries):
            if not isinstance(entry, TileMapEntry):
                raise TypeError(
                    f"Entry at index {index} is not a TileMapEntry instance."
                )

        return TileMap(
            width=width,
            height=height,
            entries=list(entries),
        )

    def clone(self, tilemap: TileMap) -> TileMap:
        """
        Create a copy of an existing TileMap.

        Args:
            tilemap: TileMap to copy.

        Returns:
            A new TileMap instance with copied entries.

        Raises:
            ValueError: If tilemap is None.
        """
        if tilemap is None:
            raise ValueError("tilemap cannot be None.")

        return TileMap(
            width=tilemap.width,
            height=tilemap.height,
            entries=list(tilemap.entries),
        )

    def _validate_dimensions(self, width: int, height: int) -> None:
        """
        Validate tile map dimensions.

        Args:
            width: Width in tiles.
            height: Height in tiles.

        Raises:
            ValueError: If dimensions are invalid.
        """
        if width <= 0:
            raise ValueError("width must be greater than 0.")

        if height <= 0:
            raise ValueError("height must be greater than 0.")
