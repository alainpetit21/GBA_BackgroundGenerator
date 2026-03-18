"""
TileMap domain model for the GBA Tile Quantizer.
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass(frozen=True)
class TileMapEntry:
    """
    Represents a single tile reference inside a tile map.
    """

    tile_index: int
    horizontal_flip: bool = False
    vertical_flip: bool = False

    def __post_init__(self) -> None:
        """
        Validate the tile map entry after initialization.
        """
        if self.tile_index < 0:
            raise ValueError("tile_index must be greater than or equal to 0.")


@dataclass
class TileMap:
    """
    Represents a 2D grid of tile references.
    """

    width: int
    height: int
    entries: list[TileMapEntry] = field(default_factory=list)

    def __post_init__(self) -> None:
        """
        Validate the tile map after initialization and fill with default entries
        if none were provided.
        """
        self._validate_dimensions()

        if not self.entries:
            self.entries = [
                TileMapEntry(tile_index=0)
                for _ in range(self.width * self.height)
            ]
        else:
            self._validate_entries()

    def _validate_dimensions(self) -> None:
        """
        Validate tile map dimensions.

        Raises:
            ValueError: If width or height is invalid.
        """
        if self.width <= 0:
            raise ValueError("width must be greater than 0.")

        if self.height <= 0:
            raise ValueError("height must be greater than 0.")

    def _validate_entries(self) -> None:
        """
        Validate the tile map entries.

        Raises:
            ValueError: If entry count is incorrect or an entry is invalid.
        """
        expected_count = self.width * self.height

        if len(self.entries) != expected_count:
            raise ValueError(
                f"TileMap must contain exactly {expected_count} entries, "
                f"but contains {len(self.entries)}."
            )

        for index, entry in enumerate(self.entries):
            if not isinstance(entry, TileMapEntry):
                raise ValueError(
                    f"TileMap entry at index {index} is not a TileMapEntry instance."
                )

    def get_entry(self, x: int, y: int) -> TileMapEntry:
        """
        Return the tile map entry at the given coordinates.

        Args:
            x: X coordinate in tile space.
            y: Y coordinate in tile space.

        Returns:
            The TileMapEntry at the given coordinates.

        Raises:
            ValueError: If the coordinates are out of range.
        """
        self._validate_coordinates(x, y)
        return self.entries[self._to_index(x, y)]

    def set_entry(self, x: int, y: int, entry: TileMapEntry) -> None:
        """
        Set the tile map entry at the given coordinates.

        Args:
            x: X coordinate in tile space.
            y: Y coordinate in tile space.
            entry: Entry to place in the map.

        Raises:
            ValueError: If the coordinates are out of range.
            TypeError: If entry is not a TileMapEntry.
        """
        self._validate_coordinates(x, y)

        if not isinstance(entry, TileMapEntry):
            raise TypeError("entry must be a TileMapEntry instance.")

        self.entries[self._to_index(x, y)] = entry

    def set_tile_index(
        self,
        x: int,
        y: int,
        tile_index: int,
        horizontal_flip: bool = False,
        vertical_flip: bool = False,
    ) -> None:
        """
        Convenience method to set a tile map entry from raw values.

        Args:
            x: X coordinate in tile space.
            y: Y coordinate in tile space.
            tile_index: Tile index in the tileset.
            horizontal_flip: Whether the tile is horizontally flipped.
            vertical_flip: Whether the tile is vertically flipped.
        """
        entry = TileMapEntry(
            tile_index=tile_index,
            horizontal_flip=horizontal_flip,
            vertical_flip=vertical_flip,
        )
        self.set_entry(x, y, entry)

    def size(self) -> int:
        """
        Return the total number of entries in the tile map.

        Returns:
            The number of tile map entries.
        """
        return len(self.entries)

    def to_rows(self) -> list[list[TileMapEntry]]:
        """
        Return the tile map as a 2D row structure.

        Returns:
            A list of rows, each containing TileMapEntry values.
        """
        rows: list[list[TileMapEntry]] = []

        for y in range(self.height):
            row_start = y * self.width
            row_end = row_start + self.width
            rows.append(self.entries[row_start:row_end])

        return rows

    def to_tile_index_rows(self) -> list[list[int]]:
        """
        Return the tile map as rows of tile indices only.

        Returns:
            A list of rows containing tile indices.
        """
        rows: list[list[int]] = []

        for row in self.to_rows():
            rows.append([entry.tile_index for entry in row])

        return rows

    def to_csv_string(self) -> str:
        """
        Export the tile map as a CSV string using tile indices only.

        Returns:
            CSV representation of the tile map.
        """
        csv_lines: list[str] = []

        for row in self.to_tile_index_rows():
            csv_lines.append(",".join(str(tile_index) for tile_index in row))

        return "\n".join(csv_lines)

    def used_tile_indices(self) -> set[int]:
        """
        Return the set of tile indices referenced by this map.

        Returns:
            A set of used tile indices.
        """
        return {entry.tile_index for entry in self.entries}

    def _to_index(self, x: int, y: int) -> int:
        """
        Convert 2D tile coordinates into a linear index.

        Args:
            x: X coordinate in tile space.
            y: Y coordinate in tile space.

        Returns:
            The linear index.
        """
        return (y * self.width) + x

    def _validate_coordinates(self, x: int, y: int) -> None:
        """
        Validate tile map coordinates.

        Args:
            x: X coordinate in tile space.
            y: Y coordinate in tile space.

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
