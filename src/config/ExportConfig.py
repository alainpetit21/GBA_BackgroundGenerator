"""
Configuration for exporting processed GBA tile data and previews.
"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class ExportConfig:
    """
    Configuration used to control which output artifacts are exported.
    """

    export_preview_png: bool = True
    export_tileset_png: bool = True
    export_tilemap_csv: bool = True
    export_palette_binary: bool = True
    export_tiles_binary: bool = True
    export_c_header: bool = False
    output_name: str = "output"

    def validate(self) -> None:
        """
        Validate the configuration values.

        Raises:
            ValueError: If one or more configuration values are invalid.
        """
        if not self.output_name.strip():
            raise ValueError("output_name cannot be empty.")

        if not any(
            [
                self.export_preview_png,
                self.export_tileset_png,
                self.export_tilemap_csv,
                self.export_palette_binary,
                self.export_tiles_binary,
                self.export_c_header,
            ]
        ):
            raise ValueError("At least one export option must be enabled.")
