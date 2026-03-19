"""
Top-level configuration object for the GBA Tile Quantizer project.
"""
from __future__ import annotations
from dataclasses import dataclass

from config.QuantizationConfig import QuantizationConfig
from config.TileReductionConfig import TileReductionConfig
from config.ExportConfig import ExportConfig


@dataclass
class ProjectConfig:
    """
    Container object grouping all configuration sections used
    during image processing and export.
    """

    quantization: QuantizationConfig
    tile_reduction: TileReductionConfig
    export: ExportConfig

    @staticmethod
    def create_default() -> "ProjectConfig":
        """
        Create a project configuration with default values.

        Returns:
            A default ProjectConfig instance.
        """
        return ProjectConfig(
            quantization=QuantizationConfig(),
            tile_reduction=TileReductionConfig(),
            export=ExportConfig(),
        )

    def validate(self) -> None:
        """
        Validate all nested configuration objects.

        Raises:
            ValueError: If any configuration section is invalid.
        """
        self.quantization.validate()
        self.tile_reduction.validate()
        self.export.validate()
