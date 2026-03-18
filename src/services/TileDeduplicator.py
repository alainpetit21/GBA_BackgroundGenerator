"""
Tile deduplication service for the GBA Tile Quantizer.
"""
from __future__ import annotations
from dataclasses import dataclass

from config.TileReductionConfig import TileReductionConfig
from domain.Tile import Tile
from domain.TileMap import TileMap, TileMapEntry
from domain.TileSet import TileSet
from domain.TileMatch import TileMatch


@dataclass
class TileDeduplicationResult:
    """
    Result of tile deduplication.
    """

    tileset: TileSet
    tilemap: TileMap


class TileDeduplicator:
    """
    Service responsible for deduplicating extracted tiles and remapping
    the tilemap to reference unique tiles.
    """

    def deduplicate(
        self,
        tiles: list[Tile],
        tilemap: TileMap,
        config: TileReductionConfig,
    ) -> TileDeduplicationResult:
        """
        Deduplicate tiles and rebuild the tilemap using unique tile references.

        Args:
            tiles: Raw extracted tiles in scan order.
            tilemap: Tile map referencing the raw extracted tiles.
            config: Tile reduction configuration.

        Returns:
            A TileDeduplicationResult containing the unique TileSet and
            remapped TileMap.

        Raises:
            ValueError: If the input is invalid.
        """
        if tiles is None:
            raise ValueError("tiles cannot be None.")

        if tilemap is None:
            raise ValueError("tilemap cannot be None.")

        if config is None:
            raise ValueError("config cannot be None.")

        config.validate()

        unique_tileset = TileSet()
        remapped_tilemap = TileMap(width=tilemap.width, height=tilemap.height)

        for y in range(tilemap.height):
            for x in range(tilemap.width):
                source_entry = tilemap.get_entry(x, y)
                source_tile = tiles[source_entry.tile_index]

                match = self._find_matching_tile(source_tile, unique_tileset, config)

                if match is None:
                    unique_tile_index = unique_tileset.add_tile(source_tile)
                    remapped_tilemap.set_entry(
                        x,
                        y,
                        TileMapEntry(
                            tile_index=unique_tile_index,
                            horizontal_flip=False,
                            vertical_flip=False,
                        ),
                    )
                else:
                    remapped_tilemap.set_entry(
                        x,
                        y,
                        TileMapEntry(
                            tile_index=match.tile_index,
                            horizontal_flip=match.horizontal_flip,
                            vertical_flip=match.vertical_flip,
                        ),
                    )

        return TileDeduplicationResult(
            tileset=unique_tileset,
            tilemap=remapped_tilemap,
        )

    def _find_matching_tile(
        self,
        source_tile: Tile,
        unique_tileset: TileSet,
        config: TileReductionConfig,
    ) -> TileMatch | None:
        """
        Find an existing matching tile in the unique tileset.

        Matching is attempted in this order:
        1. exact match
        2. horizontal flip match
        3. vertical flip match
        4. horizontal + vertical flip match

        Args:
            source_tile: Tile to match.
            unique_tileset: Current unique tileset.
            config: Tile reduction configuration.

        Returns:
            A _TileMatch if found, otherwise None.
        """
        if not config.allow_exact_deduplication:
            return None

        for tile_index, existing_tile in enumerate(unique_tileset.tiles):
            if existing_tile == source_tile:
                return TileMatch(
                    tile_index=tile_index,
                    horizontal_flip=False,
                    vertical_flip=False,
                )

            if config.allow_horizontal_flip_deduplication:
                if existing_tile.flipped_horizontal() == source_tile:
                    return TileMatch(
                        tile_index=tile_index,
                        horizontal_flip=True,
                        vertical_flip=False,
                    )

            if config.allow_vertical_flip_deduplication:
                if existing_tile.flipped_vertical() == source_tile:
                    return TileMatch(
                        tile_index=tile_index,
                        horizontal_flip=False,
                        vertical_flip=True,
                    )

            if (
                config.allow_horizontal_flip_deduplication
                and config.allow_vertical_flip_deduplication
            ):
                if existing_tile.flipped_horizontal_vertical() == source_tile:
                    return TileMatch(
                        tile_index=tile_index,
                        horizontal_flip=True,
                        vertical_flip=True,
                    )

        return None
