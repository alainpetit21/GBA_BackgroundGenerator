"""
Export service for the GBA Tile Quantizer.
"""

from __future__ import annotations
from pathlib import Path
from typing import Callable, Optional

from config.ExportConfig import ExportConfig
from domain.ProcessingResult import ProcessingResult
from services.GbaBinaryEncoder import GbaBinaryEncoder
from services.PreviewRenderer import PreviewRenderer


class ExportService:
    """
    Service responsible for exporting previews and GBA binary assets to disk.
    """

    def __init__(
        self,
        binary_encoder: GbaBinaryEncoder,
        preview_renderer: PreviewRenderer,
    ) -> None:
        """
        Initialize the export service.

        Args:
            binary_encoder: Service used to encode GBA binary data.
            preview_renderer: Service used to render preview images.
        """
        self.binary_encoder = binary_encoder
        self.preview_renderer = preview_renderer

    def export(
        self,
        result: ProcessingResult,
        output_directory: str | Path,
        config: ExportConfig,
        progress_callback: Optional[Callable[[int, str], None]] = None,
    ) -> list[Path]:
        """
        Export the processing result to disk.

        Args:
            result: Processing result to export.
            output_directory: Destination directory.
            config: Export configuration.

        Returns:
            A list of exported file paths.

        Raises:
            ValueError: If inputs are invalid.
        """
        if result is None:
            raise ValueError("result cannot be None.")

        if config is None:
            raise ValueError("config cannot be None.")

        config.validate()

        normalized_output_directory = self._normalize_output_directory(output_directory)
        normalized_output_directory.mkdir(parents=True, exist_ok=True)

        exported_files: list[Path] = []
        base_name = config.output_name.strip()
        export_steps: list[tuple[str, Path, Callable[[], None]]] = []

        if config.export_preview_png:
            preview_path = normalized_output_directory / f"{base_name}_preview.png"
            export_steps.append(
                (
                    "preview PNG",
                    preview_path,
                    lambda: self._export_preview_png(result, preview_path),
                )
            )

        if config.export_tileset_png:
            tileset_preview_path = (
                normalized_output_directory / f"{base_name}_tileset.png"
            )
            export_steps.append(
                (
                    "tileset PNG",
                    tileset_preview_path,
                    lambda: self._export_tileset_png(result, tileset_preview_path),
                )
            )

        if config.export_tilemap_csv:
            tilemap_csv_path = normalized_output_directory / f"{base_name}_tilemap.csv"
            export_steps.append(
                (
                    "tilemap CSV",
                    tilemap_csv_path,
                    lambda: self._export_tilemap_csv(result, tilemap_csv_path),
                )
            )

        if config.export_palette_binary:
            palette_binary_path = normalized_output_directory / f"{base_name}.pal.bin"
            export_steps.append(
                (
                    "palette binary",
                    palette_binary_path,
                    lambda: self._export_palette_binary(result, palette_binary_path),
                )
            )

        if config.export_tiles_binary:
            tiles_binary_path = normalized_output_directory / f"{base_name}.tiles.bin"
            export_steps.append(
                (
                    "tiles binary",
                    tiles_binary_path,
                    lambda: self._export_tiles_binary(result, tiles_binary_path),
                )
            )

            map_binary_path = normalized_output_directory / f"{base_name}.map.bin"
            export_steps.append(
                (
                    "map binary",
                    map_binary_path,
                    lambda: self._export_map_binary(result, map_binary_path),
                )
            )

        if config.export_c_header:
            c_header_path = normalized_output_directory / f"{base_name}.h"
            export_steps.append(
                (
                    "C header",
                    c_header_path,
                    lambda: self._export_c_header(result, c_header_path, base_name),
                )
            )

        self._report_progress(progress_callback, 0, "Starting export...")
        step_count = len(export_steps)
        for step_index, (step_name, output_path, action) in enumerate(export_steps, start=1):
            start_value = int(((step_index - 1) * 100) / step_count)
            self._report_progress(
                progress_callback,
                start_value,
                f"Exporting {step_name} ({step_index}/{step_count})...",
            )
            action()
            exported_files.append(output_path)
            end_value = int((step_index * 100) / step_count)
            self._report_progress(
                progress_callback,
                end_value,
                f"Exported {step_name} ({step_index}/{step_count}).",
            )

        self._report_progress(progress_callback, 100, "Export complete.")

        return exported_files

    def _report_progress(
        self,
        progress_callback: Optional[Callable[[int, str], None]],
        value: int,
        message: str,
    ) -> None:
        if progress_callback is None:
            return

        progress_callback(value, message)

    def _normalize_output_directory(self, output_directory: str | Path) -> Path:
        """
        Normalize the output directory into a Path object.

        Args:
            output_directory: Output directory to normalize.

        Returns:
            A normalized Path object.

        Raises:
            ValueError: If the output directory is empty.
        """
        if isinstance(output_directory, Path):
            normalized_output_directory = output_directory
        else:
            stripped_output_directory = output_directory.strip()
            if not stripped_output_directory:
                raise ValueError("output_directory cannot be empty.")
            normalized_output_directory = Path(stripped_output_directory)

        return normalized_output_directory

    def _export_preview_png(
        self,
        result: ProcessingResult,
        output_path: Path,
    ) -> None:
        """
        Export the reconstructed tilemap preview as PNG.

        Args:
            result: Processing result to export.
            output_path: Destination path.
        """
        image = self.preview_renderer.render_tilemap(
            tilemap=result.tilemap,
            tileset=result.tileset,
            palette_set=result.palette_set,
        )
        image.save(output_path, format="PNG")

    def _export_tileset_png(
        self,
        result: ProcessingResult,
        output_path: Path,
    ) -> None:
        """
        Export the tileset preview as PNG.

        Args:
            result: Processing result to export.
            output_path: Destination path.
        """
        image = self.preview_renderer.render_tileset(
            tileset=result.tileset,
            palette_set=result.palette_set,
            tilemap=result.tilemap,
        )
        image.save(output_path, format="PNG")

    def _export_tilemap_csv(
        self,
        result: ProcessingResult,
        output_path: Path,
    ) -> None:
        """
        Export the tilemap as CSV including tile index, palette bank, and flip flags.

        Args:
            result: Processing result to export.
            output_path: Destination path.
        """
        output_path.write_text(result.tilemap.to_csv_string(), encoding="utf-8")

    def _export_palette_binary(
        self,
        result: ProcessingResult,
        output_path: Path,
    ) -> None:
        """
        Export the palette as GBA 4bpp binary data.

        Args:
            result: Processing result to export.
            output_path: Destination path.
        """
        palette_bytes = self.binary_encoder.encode_palette_4bpp(
            palette_set=result.palette_set,
            pad_to_16=True,
        )
        output_path.write_bytes(palette_bytes)

    def _export_tiles_binary(
        self,
        result: ProcessingResult,
        output_path: Path,
    ) -> None:
        """
        Export the tileset as GBA 4bpp tile binary data.

        Args:
            result: Processing result to export.
            output_path: Destination path.
        """
        tile_bytes = self.binary_encoder.encode_tileset_4bpp(result.tileset)
        output_path.write_bytes(tile_bytes)

    def _export_map_binary(
        self,
        result: ProcessingResult,
        output_path: Path,
    ) -> None:
        """
        Export the tilemap as GBA text background map data.

        Args:
            result: Processing result to export.
            output_path: Destination path.
        """
        map_bytes = self.binary_encoder.encode_text_bg_map(
            tilemap=result.tilemap,
        )
        output_path.write_bytes(map_bytes)

    def _export_c_header(
        self,
        result: ProcessingResult,
        output_path: Path,
        base_name: str,
    ) -> None:
        """
        Export a minimal C header containing asset metadata.

        Args:
            result: Processing result to export.
            output_path: Destination path.
            base_name: Base export name.
        """
        symbol_name = self._sanitize_c_symbol(base_name)

        content = (
            f"#ifndef {symbol_name.upper()}_H\n"
            f"#define {symbol_name.upper()}_H\n\n"
            f"#define {symbol_name.upper()}_IMAGE_WIDTH {result.image_width_in_pixels()}\n"
            f"#define {symbol_name.upper()}_IMAGE_HEIGHT {result.image_height_in_pixels()}\n"
            f"#define {symbol_name.upper()}_MAP_WIDTH {result.map_width_in_tiles()}\n"
            f"#define {symbol_name.upper()}_MAP_HEIGHT {result.map_height_in_tiles()}\n"
            f"#define {symbol_name.upper()}_TILE_COUNT {result.unique_tile_count()}\n"
            f"#define {symbol_name.upper()}_PALETTE_BANK_COUNT {result.palette_bank_count()}\n"
            f"#define {symbol_name.upper()}_PALETTE_COLOR_COUNT {result.palette_color_count()}\n\n"
            f"#endif\n"
        )

        output_path.write_text(content, encoding="utf-8")

    def _sanitize_c_symbol(self, value: str) -> str:
        """
        Convert a string into a simple C-friendly symbol name.

        Args:
            value: Input string.

        Returns:
            A sanitized symbol name.
        """
        sanitized_characters: list[str] = []

        for character in value:
            if character.isalnum():
                sanitized_characters.append(character.upper())
            else:
                sanitized_characters.append("_")

        sanitized_value = "".join(sanitized_characters).strip("_")

        if not sanitized_value:
            return "OUTPUT"

        return sanitized_value
