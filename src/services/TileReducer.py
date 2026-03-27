"""
Tile reduction service for the GBA Tile Quantizer.
"""
from __future__ import annotations
from dataclasses import dataclass

from config.TileReductionConfig import TileReductionConfig
from domain.PaletteSet import PaletteSet
from domain.TileMap import TileMap, TileMapEntry
from domain.TileSet import TileSet
from domain.TileMatch import TileMatch
from services.TileSimilarityCalculator import TileSimilarityCalculator


@dataclass
class TileReductionResult:
    """
    Result of tile count reduction.
    """

    tileset: TileSet
    tilemap: TileMap


class TileReducer:
    """
    Service responsible for enforcing a maximum tile budget.
    """

    def __init__(self, similarity_calculator: TileSimilarityCalculator) -> None:
        """
        Initialize the tile reducer.

        Args:
            similarity_calculator: Service used to compare tiles.
        """
        self.similarity_calculator = similarity_calculator

    def reduce(
        self,
        tileset: TileSet,
        tilemap: TileMap,
        palette_set: PaletteSet,
        config: TileReductionConfig,
    ) -> TileReductionResult:
        """
        Reduce the tileset to fit within the configured tile budget.

        Args:
            tileset: Source unique tileset.
            tilemap: Tilemap referencing the source tileset.
            palette_set: Palette banks used for similarity scoring.
            config: Tile reduction configuration.

        Returns:
            A TileReductionResult containing the reduced tileset and remapped tilemap.

        Raises:
            ValueError: If inputs are invalid or if reduction is required but forbidden.
        """
        if tileset is None:
            raise ValueError("tileset cannot be None.")

        if tilemap is None:
            raise ValueError("tilemap cannot be None.")

        if palette_set is None:
            raise ValueError("palette_set cannot be None.")

        if config is None:
            raise ValueError("config cannot be None.")

        config.validate()

        if tileset.size() <= config.max_tiles:
            return TileReductionResult(
                tileset=tileset,
                tilemap=tilemap,
            )

        if not config.allow_lossy_reduction:
            raise ValueError(
                f"TileSet contains {tileset.size()} tiles, "
                f"which exceeds the maximum of {config.max_tiles}, "
                "and lossy reduction is disabled."
            )

        reduced_tileset = TileSet(tiles=list(tileset.tiles[:config.max_tiles]))
        reduced_tilemap = self._remap_tilemap(
            source_tileset=tileset,
            reduced_tileset=reduced_tileset,
            tilemap=tilemap,
            palette_set=palette_set,
            config=config,
        )

        return TileReductionResult(
            tileset=reduced_tileset,
            tilemap=reduced_tilemap,
        )

    def _find_best_match(
        self,
        source_tile,
        reduced_tileset: TileSet,
        palette_set: PaletteSet,
        source_palette_bank: int,
        config: TileReductionConfig,
    ) -> TileMatch:
        """
        Find the best replacement tile index in the reduced tileset.

        Args:
            source_tile: Tile to replace.
            reduced_tileset: Candidate reduced tileset.
            palette_set: Palette banks.
            source_palette_bank: Palette bank used by the source tile.
            config: Tile reduction configuration.

        Returns:
            A tuple of (best_tile_index, best_score).

        Raises:
            ValueError: If the reduced tileset is empty.
        """
        if reduced_tileset.is_empty():
            raise ValueError("Cannot find a replacement in an empty reduced tileset.")

        best_tile_index = 0
        best_score = self.similarity_calculator.calculate(
            first_tile=source_tile,
            second_tile=reduced_tileset.get_tile(0),
            metric=config.similarity_metric,
            first_palette=palette_set.get_palette(source_palette_bank),
            second_palette=palette_set.get_palette(source_palette_bank),
        )

        for tile_index in range(1, reduced_tileset.size()):
            candidate_tile = reduced_tileset.get_tile(tile_index)
            candidate_score = self.similarity_calculator.calculate(
                first_tile=source_tile,
                second_tile=candidate_tile,
                metric=config.similarity_metric,
                first_palette=palette_set.get_palette(source_palette_bank),
                second_palette=palette_set.get_palette(source_palette_bank),
            )

            if candidate_score < best_score:
                best_tile_index = tile_index
                best_score = candidate_score

        return TileMatch(
            tile_index=best_tile_index,
            horizontal_flip=False,
            vertical_flip=False,
            score=best_score,
        )

    def _remap_tilemap(
        self,
        source_tileset: TileSet,
        reduced_tileset: TileSet,
        tilemap: TileMap,
        palette_set: PaletteSet,
        config: TileReductionConfig,
    ) -> TileMap:
        """
        Rebuild the tilemap using the reduced tileset.

        Existing flip and palette-bank flags are preserved.

        Args:
            source_tileset: Original tileset.
            reduced_tileset: Reduced tileset.
            tilemap: Original tilemap.
            palette_set: Palette banks.
            config: Tile reduction configuration.

        Returns:
            A new remapped TileMap.
        """
        remapped_tilemap = TileMap(width=tilemap.width, height=tilemap.height)

        for y in range(tilemap.height):
            for x in range(tilemap.width):
                original_entry = tilemap.get_entry(x, y)
                remapped_index = original_entry.tile_index

                if original_entry.tile_index >= reduced_tileset.size():
                    source_tile = source_tileset.get_tile(original_entry.tile_index)
                    best_match = self._find_best_match(
                        source_tile=source_tile,
                        reduced_tileset=reduced_tileset,
                        palette_set=palette_set,
                        source_palette_bank=original_entry.palette_bank,
                        config=config,
                    )

                    if best_match.score > config.error_threshold > 0.0:
                        raise ValueError(
                            f"No acceptable replacement found for tile {original_entry.tile_index}. "
                            f"Best score was {best_match.score}, "
                            f"which exceeds error_threshold={config.error_threshold}."
                        )

                    remapped_index = best_match.tile_index

                remapped_tilemap.set_entry(
                    x,
                    y,
                    TileMapEntry(
                        tile_index=remapped_index,
                        horizontal_flip=original_entry.horizontal_flip,
                        vertical_flip=original_entry.vertical_flip,
                        palette_bank=original_entry.palette_bank,
                    ),
                )

        return remapped_tilemap
