"""
Tile extraction service for the GBA Tile Quantizer.
"""
from __future__ import annotations
from dataclasses import dataclass

from domain.IndexedImage import IndexedImage
from domain.Tile import Tile
from domain.TileMap import TileMap


@dataclass
class TileExtractionResult:
    """
    Result of extracting tiles from an indexed image.
    """

    tiles: list[Tile]
    tilemap: TileMap


class TileExtractor:
    """
    Service responsible for extracting 8x8 tiles from an indexed image.
    """

    def extract(
        self,
        indexed_image: IndexedImage,
        tile_width: int = 8,
        tile_height: int = 8,
    ) -> TileExtractionResult:
        """
        Extract tiles from an indexed image in scan order.

        Args:
            indexed_image: Indexed image to split into tiles.
            tile_width: Tile width in pixels.
            tile_height: Tile height in pixels.

        Returns:
            A TileExtractionResult containing the extracted tiles and
            a tilemap referencing them in scan order.

        Raises:
            ValueError: If the indexed image is not tile-aligned or
                        if tile dimensions are invalid.
        """
        if indexed_image is None:
            raise ValueError("indexed_image cannot be None.")

        if tile_width <= 0:
            raise ValueError("tile_width must be greater than 0.")

        if tile_height <= 0:
            raise ValueError("tile_height must be greater than 0.")

        if tile_width != 8:
            raise ValueError("tile_width must be 8 in v1.")

        if tile_height != 8:
            raise ValueError("tile_height must be 8 in v1.")

        if not indexed_image.is_tile_aligned(tile_width, tile_height):
            raise ValueError(
                "Indexed image dimensions must be aligned to the tile grid."
            )

        map_width = indexed_image.tile_width_in_tiles(tile_width)
        map_height = indexed_image.tile_height_in_tiles(tile_height)

        tiles: list[Tile] = []
        tilemap = TileMap(width=map_width, height=map_height)

        tile_index = 0

        for tile_y in range(map_height):
            for tile_x in range(map_width):
                tile = self._extract_single_tile(
                    indexed_image=indexed_image,
                    tile_x=tile_x,
                    tile_y=tile_y,
                    tile_width=tile_width,
                    tile_height=tile_height,
                )

                tiles.append(tile)
                tilemap.set_tile_index(tile_x, tile_y, tile_index)
                tile_index += 1

        return TileExtractionResult(
            tiles=tiles,
            tilemap=tilemap,
        )

    def _extract_single_tile(
        self,
        indexed_image: IndexedImage,
        tile_x: int,
        tile_y: int,
        tile_width: int,
        tile_height: int,
    ) -> Tile:
        """
        Extract a single tile from the indexed image.

        Args:
            indexed_image: Source indexed image.
            tile_x: Tile X coordinate in tile space.
            tile_y: Tile Y coordinate in tile space.
            tile_width: Tile width in pixels.
            tile_height: Tile height in pixels.

        Returns:
            The extracted Tile.
        """
        start_x = tile_x * tile_width
        start_y = tile_y * tile_height

        rows: list[list[int]] = []

        for local_y in range(tile_height):
            row: list[int] = []

            for local_x in range(tile_width):
                pixel_x = start_x + local_x
                pixel_y = start_y + local_y
                row.append(indexed_image.get_pixel(pixel_x, pixel_y))

            rows.append(row)

        return Tile.from_rows(rows)
