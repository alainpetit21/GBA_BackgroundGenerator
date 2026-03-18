"""
Tile reduction service for the GBA Tile Quantizer.
"""
from __future__ import annotations
from dataclasses import dataclass

from config.TileReductionConfig import TileReductionConfig
from domain.Palette import Palette
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
        palette: Palette,
        config: TileReductionConfig,
    ) -> TileReductionResult:
        """
        Reduce the tileset to fit within the configured tile budget.

        Args:
            tileset: Source unique tileset.
            tilemap: Tilemap referencing the source tileset.
            palette: Shared palette for similarity scoring.
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

        if palette is None:
            raise ValueError("palette cannot be None.")

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
        index_remap = self._build_index_remap(
            source_tileset=tileset,
            reduced_tileset=reduced_tileset,
            palette=palette,
            config=config,
        )
        reduced_tilemap = self._remap_tilemap(tilemap, index_remap)

        return TileReductionResult(
            tileset=reduced_tileset,
            tilemap=reduced_tilemap,
        )

    def _build_index_remap(
        self,
        source_tileset: TileSet,
        reduced_tileset: TileSet,
        palette: Palette,
        config: TileReductionConfig,
    ) -> dict[int, int]:
        """
        Build a mapping from original tile indices to reduced tile indices.

        Args:
            source_tileset: Original tileset.
            reduced_tileset: Reduced tileset containing only kept tiles.
            palette: Shared palette.
            config: Tile reduction configuration.

        Returns:
            A dictionary mapping old tile indices to new tile indices.

        Raises:
            ValueError: If no suitable replacement is found.
        """
        index_remap: dict[int, int] = {}

        # Tiles that remain in the reduced bank map to themselves.
        for tile_index in range(reduced_tileset.size()):
            index_remap[tile_index] = tile_index

        # Tiles beyond the budget must be approximated.
        for source_index in range(reduced_tileset.size(), source_tileset.size()):
            source_tile = source_tileset.get_tile(source_index)

            best_match = self._find_best_match(
                source_tile=source_tile,
                reduced_tileset=reduced_tileset,
                palette=palette,
                config=config,
            )

            if best_match.score > config.error_threshold > 0.0:
                raise ValueError(
                    f"No acceptable replacement found for tile {source_index}. "
                    f"Best score was {best_match.score}, "
                    f"which exceeds error_threshold={config.error_threshold}."
                )

            index_remap[source_index] = best_match.tile_index

        return index_remap

    def _find_best_match(
        self,
        source_tile,
        reduced_tileset: TileSet,
        palette: Palette,
        config: TileReductionConfig,
    ) -> TileMatch:
        """
        Find the best replacement tile index in the reduced tileset.

        Args:
            source_tile: Tile to replace.
            reduced_tileset: Candidate reduced tileset.
            palette: Shared palette.
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
            palette=palette,
        )

        for tile_index in range(1, reduced_tileset.size()):
            candidate_tile = reduced_tileset.get_tile(tile_index)
            candidate_score = self.similarity_calculator.calculate(
                first_tile=source_tile,
                second_tile=candidate_tile,
                metric=config.similarity_metric,
                palette=palette,
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
        tilemap: TileMap,
        index_remap: dict[int, int],
    ) -> TileMap:
        """
        Rebuild the tilemap using the reduced tile index mapping.

        Existing flip flags are preserved.

        Args:
            tilemap: Original tilemap.
            index_remap: Mapping from original tile indices to reduced indices.

        Returns:
            A new remapped TileMap.
        """
        remapped_tilemap = TileMap(width=tilemap.width, height=tilemap.height)

        for y in range(tilemap.height):
            for x in range(tilemap.width):
                original_entry = tilemap.get_entry(x, y)
                remapped_index = index_remap[original_entry.tile_index]

                remapped_tilemap.set_entry(
                    x,
                    y,
                    TileMapEntry(
                        tile_index=remapped_index,
                        horizontal_flip=original_entry.horizontal_flip,
                        vertical_flip=original_entry.vertical_flip,
                    ),
                )

        return remapped_tilemap
