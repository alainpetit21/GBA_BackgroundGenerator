"""
TileSet domain model for the GBA Tile Quantizer.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from domain.Tile import Tile
from domain.TileMatch import TileMatch


@dataclass
class TileSet:
    """
    Represents a collection of unique 8x8 tiles.
    """

    tiles: list[Tile] = field(default_factory=list)

    def __post_init__(self) -> None:
        """
        Validate the tileset after initialization.
        """
        self._validate_tiles()

    def _validate_tiles(self) -> None:
        """
        Validate the tileset contents.

        Raises:
            ValueError: If any element is not a Tile.
        """
        for index, tile in enumerate(self.tiles):
            if not isinstance(tile, Tile):
                raise ValueError(f"Element at index {index} is not a Tile instance.")

    def add_tile(self, tile: Tile) -> int:
        """
        Add a tile to the tileset.

        Args:
            tile: Tile to add.

        Returns:
            The index of the newly added tile.

        Raises:
            TypeError: If tile is not a Tile.
        """
        if not isinstance(tile, Tile):
            raise TypeError("tile must be a Tile instance.")

        self.tiles.append(tile)
        return len(self.tiles) - 1

    def get_tile(self, index: int) -> Tile:
        """
        Return a tile by index.

        Args:
            index: Tile index.

        Returns:
            The tile at the given index.

        Raises:
            IndexError: If the index is out of range.
        """
        return self.tiles[index]

    def find_exact_match(self, tile: Tile) -> int | None:
        """
        Find an exact tile match in the tileset.

        Args:
            tile: Tile to search for.

        Returns:
            The tile index if found, otherwise None.

        Raises:
            TypeError: If tile is not a Tile.
        """
        if not isinstance(tile, Tile):
            raise TypeError("tile must be a Tile instance.")

        for index, existing_tile in enumerate(self.tiles):
            if existing_tile == tile:
                return index

        return None

    def contains(self, tile: Tile) -> bool:
        """
        Check whether the tileset contains the given tile.

        Args:
            tile: Tile to search for.

        Returns:
            True if the tile exists in the tileset, otherwise False.
        """
        return self.find_exact_match(tile) is not None

    def size(self) -> int:
        """
        Return the number of tiles in the tileset.

        Returns:
            The number of tiles.
        """
        return len(self.tiles)

    def is_empty(self) -> bool:
        """
        Check whether the tileset is empty.

        Returns:
            True if the tileset contains no tiles, otherwise False.
        """
        return len(self.tiles) == 0

    def clear(self) -> None:
        """
        Remove all tiles from the tileset.
        """
        self.tiles.clear()

    def to_4bpp_binary(self) -> bytes:
        """
        Encode the entire tileset as concatenated GBA 4bpp tile data.

        Returns:
            Binary data for all tiles in the tileset.
        """
        output = bytearray()

        for tile in self.tiles:
            output.extend(tile.to_4bpp_binary())

        return bytes(output)

    def unique_tile_count(self) -> int:
        """
        Return the number of unique tiles in the tileset.

        Since TileSet is intended to already contain unique tiles,
        this is equivalent to size() in normal usage.

        Returns:
            The number of tiles.
        """
        return len(self.tiles)

    def validate_max_size(self, max_tiles: int) -> None:
        """
        Validate that the tileset does not exceed the specified maximum size.

        Args:
            max_tiles: Maximum allowed number of tiles.

        Raises:
            ValueError: If the tileset exceeds the maximum size.
        """
        if max_tiles <= 0:
            raise ValueError("max_tiles must be greater than 0.")

        if len(self.tiles) > max_tiles:
            raise ValueError(
                f"TileSet contains {len(self.tiles)} tiles, "
                f"which exceeds the maximum of {max_tiles}."
            )

    def find_best_match(self, tile: Tile) -> TileMatch | None:
        """
        Find the closest matching tile using the Tile.difference_score metric.

        Args:
            tile: Tile to compare.

        Returns:
            A TileMatch, or None if the tileset is empty.

        Raises:
            TypeError: If tile is not a Tile.
        """
        if not isinstance(tile, Tile):
            raise TypeError("tile must be a Tile instance.")

        if self.is_empty():
            return None

        best_index = 0
        best_score = self.tiles[0].difference_score(tile)

        for index in range(1, len(self.tiles)):
            score = self.tiles[index].difference_score(tile)
            if score < best_score:
                best_index = index
                best_score = score

        return TileMatch(
            tile_index=best_index,
            horizontal_flip=False,
            vertical_flip=False,
            score=best_score,
        )
