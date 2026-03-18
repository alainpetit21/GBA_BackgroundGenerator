"""
Configuration for tile deduplication and tile count reduction.
"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class TileReductionConfig:
    """
    Configuration used to control tile deduplication and lossy reduction.
    """

    max_tiles: int = 256
    allow_exact_deduplication: bool = True
    allow_horizontal_flip_deduplication: bool = True
    allow_vertical_flip_deduplication: bool = True
    allow_lossy_reduction: bool = True
    similarity_metric: str = "rgb_weighted"
    error_threshold: float = 0.0

    def validate(self) -> None:
        """
        Validate the configuration values.

        Raises:
            ValueError: If one or more configuration values are invalid.
        """
        if self.max_tiles <= 0:
            raise ValueError("max_tiles must be greater than 0.")

        if self.max_tiles > 1024:
            raise ValueError("max_tiles must be 1024 or less for GBA tile indexing.")

        if not self.allow_exact_deduplication and (
            self.allow_horizontal_flip_deduplication
            or self.allow_vertical_flip_deduplication
        ):
            raise ValueError(
                "Flip deduplication requires exact deduplication to be enabled."
            )

        valid_metrics = {
            "index_difference",
            "rgb_euclidean",
            "rgb_weighted",
        }
        if self.similarity_metric not in valid_metrics:
            raise ValueError(
                "similarity_metric must be one of: "
                f"{', '.join(sorted(valid_metrics))}."
            )

        if self.error_threshold < 0.0:
            raise ValueError("error_threshold must be greater than or equal to 0.0.")
