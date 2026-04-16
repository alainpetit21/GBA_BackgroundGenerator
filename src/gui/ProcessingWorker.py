"""
Background worker used to process images without blocking the GUI thread.
"""

from __future__ import annotations

from pathlib import Path
import traceback

from PySide6.QtCore import QObject, Signal, Slot

from config.ProjectConfig import ProjectConfig
from domain.ProcessingResult import ProcessingResult
from services.ProcessingPipeline import ProcessingPipeline


class ProcessingWorker(QObject):
    """
    Execute image processing in a background thread and emit progress updates.
    """

    progress_changed = Signal(int, str)
    finished = Signal(object, str)
    failed = Signal(object)

    def __init__(
        self,
        processing_pipeline: ProcessingPipeline,
        image_path: Path,
        config: ProjectConfig,
    ) -> None:
        super().__init__()
        self.processing_pipeline = processing_pipeline
        self.image_path = image_path
        self.config = config

    @Slot()
    def run(self) -> None:
        """
        Run the processing pipeline and emit the result back to the GUI thread.
        """
        try:
            result = self.processing_pipeline.process(
                image_path=self.image_path,
                config=self.config,
                progress_callback=self.progress_changed.emit,
            )
            message = f"Processing complete. {result.summary()}"
            self.finished.emit(result, message)
        except Exception as exception:  # noqa: BLE001
            self.failed.emit(
                {
                    "message": str(exception),
                    "exception_type": type(exception).__name__,
                    "traceback": traceback.format_exc(),
                    "image_path": str(self.image_path),
                    "source": "ProcessingWorker.run",
                },
            )
