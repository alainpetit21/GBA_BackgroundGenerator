"""
Processing pipeline service for the GBA Tile Quantizer.
"""

from __future__ import annotations
from pathlib import Path
from typing import Callable, Optional

from config.ProjectConfig import ProjectConfig
from domain.ProcessingResult import ProcessingResult
from services.ImageLoader import ImageLoader
from services.ImagePreprocessor import ImagePreprocessor
from services.PaletteQuantizer import PaletteQuantizer
from services.PreviewRenderer import PreviewRenderer
from services.TileDeduplicator import TileDeduplicator
from services.TileExtractor import TileExtractor
from services.TileReducer import TileReducer


class ProcessingPipeline:
    """
    High-level orchestration service for the full image-to-GBA pipeline.
    """

    def __init__(
        self,
        image_loader: ImageLoader,
        image_preprocessor: ImagePreprocessor,
        palette_quantizer: PaletteQuantizer,
        tile_extractor: TileExtractor,
        tile_deduplicator: TileDeduplicator,
        tile_reducer: TileReducer,
        preview_renderer: PreviewRenderer,
    ) -> None:
        """
        Initialize the processing pipeline.

        Args:
            image_loader: Service used to load images from disk.
            image_preprocessor: Service used to preprocess source images.
            palette_quantizer: Service used to quantize RGB images to indexed images.
            tile_extractor: Service used to extract raw 8x8 tiles.
            tile_deduplicator: Service used to deduplicate raw tiles.
            tile_reducer: Service used to enforce a maximum tile budget.
            preview_renderer: Service used to render preview images.
        """
        self.image_loader = image_loader
        self.image_preprocessor = image_preprocessor
        self.palette_quantizer = palette_quantizer
        self.tile_extractor = tile_extractor
        self.tile_deduplicator = tile_deduplicator
        self.tile_reducer = tile_reducer
        self.preview_renderer = preview_renderer

    def process(
        self,
        image_path: str | Path,
        config: ProjectConfig,
        progress_callback: Optional[Callable[[int, str], None]] = None,
    ) -> ProcessingResult:
        """
        Run the full processing pipeline for a single image.

        Args:
            image_path: Path to the source image.
            config: Project configuration.

        Returns:
            A ProcessingResult containing the final processed assets.

        Raises:
            ValueError: If config is invalid.
        """
        if config is None:
            raise ValueError("config cannot be None.")

        config.validate()
        self._report_progress(progress_callback, 0, "Starting processing...")

        source_image = self.image_loader.load(image_path)
        self._report_progress(progress_callback, 10, "Loaded source image.")

        preprocessed_image = self.image_preprocessor.preprocess(
            image=source_image,
            config=config.quantization,
        )
        self._report_progress(progress_callback, 25, "Preprocessed image.")

        quantized_image = self.palette_quantizer.quantize(
            image=preprocessed_image,
            config=config.quantization,
        )
        self._report_progress(progress_callback, 45, "Quantized palette.")

        deduplication_result = self.tile_deduplicator.deduplicate(
            tiles=quantized_image.tiles,
            tilemap=quantized_image.tilemap,
            config=config.tile_reduction,
        )
        self._report_progress(progress_callback, 60, "Deduplicated tiles.")

        reduction_result = self.tile_reducer.reduce(
            tileset=deduplication_result.tileset,
            tilemap=deduplication_result.tilemap,
            palette_set=quantized_image.palette_set,
            config=config.tile_reduction,
        )
        self._report_progress(progress_callback, 78, "Reduced tileset.")

        preview_image_bytes = self.preview_renderer.render_tilemap_to_png_bytes(
            tilemap=reduction_result.tilemap,
            tileset=reduction_result.tileset,
            palette_set=quantized_image.palette_set,
        )
        self._report_progress(progress_callback, 93, "Rendered map preview.")

        tileset_preview_image_bytes = self.preview_renderer.render_tileset_to_png_bytes(
            tileset=reduction_result.tileset,
            palette_set=quantized_image.palette_set,
            tilemap=reduction_result.tilemap,
        )
        self._report_progress(progress_callback, 100, "Rendered tileset preview.")

        return ProcessingResult(
            image_width=quantized_image.image_width,
            image_height=quantized_image.image_height,
            palette_set=quantized_image.palette_set,
            tileset=reduction_result.tileset,
            tilemap=reduction_result.tilemap,
            preview_image_bytes=preview_image_bytes,
            tileset_preview_image_bytes=tileset_preview_image_bytes,
        )

    def _report_progress(
        self,
        progress_callback: Optional[Callable[[int, str], None]],
        value: int,
        message: str,
    ) -> None:
        """
        Emit a progress update if a callback is provided.
        """
        if progress_callback is None:
            return

        progress_callback(value, message)
