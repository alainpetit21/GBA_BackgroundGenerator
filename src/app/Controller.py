"""
Application controller for the GBA Tile Quantizer.

This class acts as the bridge between the GUI layer and the
processing/services layer. In v1, it provides the basic actions
the UI can trigger and stores the current application state.
"""
from __future__ import annotations
from pathlib import Path
from typing import Optional

from config.ExportConfig import ExportConfig
from config.ProjectConfig import ProjectConfig
from config.QuantizationConfig import QuantizationConfig
from config.TileReductionConfig import TileReductionConfig
from domain.ProcessingResult import ProcessingResult
from services.ExportService import ExportService
from services.GbaBinaryEncoder import GbaBinaryEncoder
from services.ImageLoader import ImageLoader
from services.ImagePreprocessor import ImagePreprocessor
from services.PaletteQuantizer import PaletteQuantizer
from services.PreviewRenderer import PreviewRenderer
from services.ProcessingPipeline import ProcessingPipeline
from services.TileDeduplicator import TileDeduplicator
from services.TileExtractor import TileExtractor
from services.TileReducer import TileReducer
from services.TileSimilarityCalculator import TileSimilarityCalculator


class Controller:
    """
    Coordinates user actions coming from the GUI and delegates work
    to the processing pipeline and export services.

    In this first version, the controller manages only the core
    application state and returns status messages for the GUI.
    """

    def __init__(self) -> None:
        """
        Initialize the controller state.
        """
        self.current_image_path: Optional[Path] = None
        self.current_result = None
        self.project_config = self._create_default_project_config()

        self.preview_renderer = PreviewRenderer()
        self.binary_encoder = GbaBinaryEncoder()
        self.tile_similarity_calculator = TileSimilarityCalculator()

        self.processing_pipeline = ProcessingPipeline(
            image_loader=ImageLoader(),
            image_preprocessor=ImagePreprocessor(),
            palette_quantizer=PaletteQuantizer(),
            tile_extractor=TileExtractor(),
            tile_deduplicator=TileDeduplicator(),
            tile_reducer=TileReducer(self.tile_similarity_calculator),
            preview_renderer=self.preview_renderer,
        )

        self.export_service = ExportService(
            binary_encoder=self.binary_encoder,
            preview_renderer=self.preview_renderer,
        )

    def load_image(self, image_path: str) -> str:
        """
        Register the image selected by the user.

        Args:
            image_path: Path to the source image.

        Returns:
            A status message suitable for display in the GUI.

        Raises:
            ValueError: If the provided path is empty.
            FileNotFoundError: If the file does not exist.
        """
        normalized_path = image_path.strip()

        if not normalized_path:
            raise ValueError("Image path cannot be empty.")

        path = Path(normalized_path)

        if not path.exists():
            raise FileNotFoundError(f"Image file not found: {path}")

        if not path.is_file():
            raise FileNotFoundError(f"Path is not a file: {path}")

        self.current_image_path = path
        self.current_result = None

        return f"Loaded image: {path}"

    def process_image(self) -> str:
        """
        Process the currently loaded image.

        In the current skeleton version, this method only validates
        that an image is loaded. Later it will invoke the
        ProcessingPipeline.

        Returns:
            A status message suitable for display in the GUI.

        Raises:
            RuntimeError: If no image has been loaded.
        """
        if self.current_image_path is None:
            raise RuntimeError("No image loaded.")

        self.project_config.validate()

        self.current_result = self.processing_pipeline.process(
            image_path=self.current_image_path,
            config=self.project_config,
        )

        return f"Processing complete. {self.current_result.summary()}"

    def build_processing_request(self) -> tuple[Path, ProjectConfig]:
        """
        Build a validated processing request for background execution.

        Returns:
            The image path and project configuration to process.
        """
        if self.current_image_path is None:
            raise RuntimeError("No image loaded.")

        self.project_config.validate()
        return self.current_image_path, self.project_config

    def set_current_result(self, result: ProcessingResult) -> None:
        """
        Store a processing result produced outside of the controller.

        Args:
            result: The newly computed processing result.
        """
        if result is None:
            raise ValueError("result cannot be None.")

        self.current_result = result

    def export_result(self, output_directory: str) -> str:
        """
        Export the current processing result.

        In the current skeleton version, this validates the request
        and will later call the ExportService.

        Args:
            output_directory: Directory where files should be exported.

        Returns:
            A status message suitable for display in the GUI.

        Raises:
            RuntimeError: If there is no processing result available.
            ValueError: If the output directory is empty.
        """
        normalized_output_directory = output_directory.strip()

        if not normalized_output_directory:
            raise ValueError("Output directory cannot be empty.")

        if self.current_result is None:
            raise RuntimeError("Nothing to export. Process an image first.")

        exported_files = self.export_service.export(
            result=self.current_result,
            output_directory=normalized_output_directory,
            config=self.project_config.export,
        )

        return f"Export complete. Wrote {len(exported_files)} file(s)."

    def get_current_image_path(self) -> Optional[Path]:
        """
        Return the currently loaded image path.

        Returns:
            The current image path, or None if no image is loaded.
        """
        return self.current_image_path

    def get_current_result(self) -> Optional[ProcessingResult]:
        """
        Return the current processing result.

        Returns:
            The current processing result, or None if nothing has been processed.
        """
        return self.current_result

    def has_loaded_image(self) -> bool:
        """
        Indicate whether an image is currently loaded.

        Returns:
            True if an image is loaded, otherwise False.
        """
        return self.current_image_path is not None

    def has_result(self) -> bool:
        """
        Indicate whether a processed result is available.

        Returns:
            True if a processing result is available, otherwise False.
        """
        return self.current_result is not None

    def _create_default_project_config(self) -> ProjectConfig:
        """
        Create the default project configuration for v1.

        Returns:
            A default ProjectConfig instance.
        """
        return ProjectConfig(
            quantization=QuantizationConfig(
                palette_bank_count=1,
                dithering_enabled=False,
                quantization_method="median_cut",
                tile_width=8,
                tile_height=8,
                pad_to_tile_grid=True,
            ),
            tile_reduction=TileReductionConfig(
                max_tiles=256,
                allow_exact_deduplication=True,
                allow_horizontal_flip_deduplication=True,
                allow_vertical_flip_deduplication=True,
                allow_lossy_reduction=True,
                similarity_metric="rgb_weighted",
                error_threshold=0.0,
            ),
            export=ExportConfig(
                export_preview_png=True,
                export_tileset_png=True,
                export_tilemap_csv=True,
                export_palette_binary=True,
                export_tiles_binary=True,
                export_c_header=False,
                output_name="output",
            ),
        )

    def set_project_config(self, config: ProjectConfig) -> None:
        """
        Replace the current project configuration.

        Args:
            config: New project configuration.
        """
        if config is None:
            raise ValueError("config cannot be None.")

        config.validate()
        self.project_config = config
