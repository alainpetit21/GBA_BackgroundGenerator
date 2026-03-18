"""
Tile similarity calculation service for the GBA Tile Quantizer.
"""
from __future__ import annotations
from domain.Palette import Palette
from domain.Tile import Tile


class TileSimilarityCalculator:
    """
    Service responsible for computing similarity scores between tiles.
    """

    def calculate(
        self,
        first_tile: Tile,
        second_tile: Tile,
        metric: str,
        palette: Palette,
    ) -> int:
        """
        Calculate a similarity score between two tiles.

        Lower scores indicate more similar tiles.
        A score of 0 means the tiles are identical under the chosen metric.

        Args:
            first_tile: First tile to compare.
            second_tile: Second tile to compare.
            metric: Similarity metric name.
            palette: Palette used to interpret palette indices as RGB colors.

        Returns:
            An integer similarity score.

        Raises:
            ValueError: If the metric is unsupported.
            TypeError: If inputs are invalid.
        """
        if not isinstance(first_tile, Tile):
            raise TypeError("first_tile must be a Tile instance.")

        if not isinstance(second_tile, Tile):
            raise TypeError("second_tile must be a Tile instance.")

        if not isinstance(palette, Palette):
            raise TypeError("palette must be a Palette instance.")

        if metric == "index_difference":
            return self._calculate_index_difference(first_tile, second_tile)

        if metric == "rgb_euclidean":
            return self._calculate_rgb_euclidean(first_tile, second_tile, palette)

        if metric == "rgb_weighted":
            return self._calculate_rgb_weighted(first_tile, second_tile, palette)

        raise ValueError(f"Unsupported similarity metric: {metric}")

    def _calculate_index_difference(
        self,
        first_tile: Tile,
        second_tile: Tile,
    ) -> int:
        """
        Calculate similarity using absolute palette-index differences.

        Args:
            first_tile: First tile to compare.
            second_tile: Second tile to compare.

        Returns:
            Sum of absolute palette-index differences.
        """
        score = 0

        for first_pixel, second_pixel in zip(first_tile.pixels, second_tile.pixels):
            score += abs(first_pixel - second_pixel)

        return score

    def _calculate_rgb_euclidean(
        self,
        first_tile: Tile,
        second_tile: Tile,
        palette: Palette,
    ) -> int:
        """
        Calculate similarity using squared Euclidean RGB distance.

        Args:
            first_tile: First tile to compare.
            second_tile: Second tile to compare.
            palette: Palette used to resolve indices into RGB values.

        Returns:
            Sum of squared RGB distances across all pixels.
        """
        score = 0

        for first_pixel, second_pixel in zip(first_tile.pixels, second_tile.pixels):
            first_color = palette.get_color(first_pixel)
            second_color = palette.get_color(second_pixel)

            red_difference = first_color[0] - second_color[0]
            green_difference = first_color[1] - second_color[1]
            blue_difference = first_color[2] - second_color[2]

            score += (
                (red_difference * red_difference)
                + (green_difference * green_difference)
                + (blue_difference * blue_difference)
            )

        return score

    def _calculate_rgb_weighted(
        self,
        first_tile: Tile,
        second_tile: Tile,
        palette: Palette,
    ) -> int:
        """
        Calculate similarity using weighted squared RGB distance.

        Green differences are weighted more heavily because the human eye
        tends to be more sensitive to green variation.

        Args:
            first_tile: First tile to compare.
            second_tile: Second tile to compare.
            palette: Palette used to resolve indices into RGB values.

        Returns:
            Sum of weighted squared RGB distances across all pixels.
        """
        score = 0

        for first_pixel, second_pixel in zip(first_tile.pixels, second_tile.pixels):
            first_color = palette.get_color(first_pixel)
            second_color = palette.get_color(second_pixel)

            red_difference = first_color[0] - second_color[0]
            green_difference = first_color[1] - second_color[1]
            blue_difference = first_color[2] - second_color[2]

            score += (
                (2 * red_difference * red_difference)
                + (4 * green_difference * green_difference)
                + (3 * blue_difference * blue_difference)
            )

        return score
