"""
Configuration panel widget for the GBA Tile Quantizer.
"""
from __future__ import annotations
from typing import Optional
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QCheckBox, QComboBox, QFormLayout, QGroupBox, QLineEdit, QSpinBox, QVBoxLayout, QWidget

from config.ExportConfig import ExportConfig
from config.ProjectConfig import ProjectConfig
from config.QuantizationConfig import QuantizationConfig
from config.TileReductionConfig import TileReductionConfig


class ConfigPanelWidget(QWidget):
    """
    Widget used to view and edit the current ProjectConfig.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.palette_bank_count_spin_box: Optional[QSpinBox] = None
        self.dithering_check_box: Optional[QCheckBox] = None
        self.pad_to_tile_grid_check_box: Optional[QCheckBox] = None

        self.max_tiles_spin_box: Optional[QSpinBox] = None
        self.allow_exact_deduplication_check_box: Optional[QCheckBox] = None
        self.allow_horizontal_flip_deduplication_check_box: Optional[QCheckBox] = None
        self.allow_vertical_flip_deduplication_check_box: Optional[QCheckBox] = None
        self.allow_lossy_reduction_check_box: Optional[QCheckBox] = None
        self.similarity_metric_combo_box: Optional[QComboBox] = None

        self.output_name_line_edit: Optional[QLineEdit] = None
        self.export_preview_png_check_box: Optional[QCheckBox] = None
        self.export_tileset_png_check_box: Optional[QCheckBox] = None
        self.export_tilemap_csv_check_box: Optional[QCheckBox] = None
        self.export_palette_binary_check_box: Optional[QCheckBox] = None
        self.export_tiles_binary_check_box: Optional[QCheckBox] = None
        self.export_c_header_check_box: Optional[QCheckBox] = None

        self._build_ui()

    def _build_ui(self) -> None:
        """
        Build the full configuration panel UI.
        """
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(main_layout)

        main_layout.addWidget(self._create_quantization_group_box())
        main_layout.addWidget(self._create_tile_reduction_group_box())
        main_layout.addWidget(self._create_export_group_box())
        main_layout.addStretch()

    def _create_quantization_group_box(self) -> QGroupBox:
        """
        Create the quantization settings group.

        Returns:
            The configured group box.
        """
        group_box = QGroupBox("Quantization")
        form_layout = QFormLayout()
        group_box.setLayout(form_layout)

        self.palette_bank_count_spin_box = QSpinBox()
        self.palette_bank_count_spin_box.setRange(1, 16)
        self.palette_bank_count_spin_box.setToolTip(
            "Number of 16-color 4bpp palette banks available to the background."
        )

        self.dithering_check_box = QCheckBox()
        self.pad_to_tile_grid_check_box = QCheckBox()

        form_layout.addRow("Palette banks (max 16)", self.palette_bank_count_spin_box)
        form_layout.addRow("Dithering", self.dithering_check_box)
        form_layout.addRow("Pad to tile grid", self.pad_to_tile_grid_check_box)

        return group_box

    def _create_tile_reduction_group_box(self) -> QGroupBox:
        """
        Create the tile reduction settings group.

        Returns:
            The configured group box.
        """
        group_box = QGroupBox("Tile Reduction")
        form_layout = QFormLayout()
        group_box.setLayout(form_layout)

        self.max_tiles_spin_box = QSpinBox()
        self.max_tiles_spin_box.setRange(1, 1024)

        self.allow_exact_deduplication_check_box = QCheckBox()
        self.allow_horizontal_flip_deduplication_check_box = QCheckBox()
        self.allow_vertical_flip_deduplication_check_box = QCheckBox()
        self.allow_lossy_reduction_check_box = QCheckBox()

        self.similarity_metric_combo_box = QComboBox()
        self.similarity_metric_combo_box.addItems(
            [
                "index_difference",
                "rgb_euclidean",
                "rgb_weighted",
            ]
        )

        form_layout.addRow("Max tiles", self.max_tiles_spin_box)
        form_layout.addRow(
            "Exact deduplication",
            self.allow_exact_deduplication_check_box,
        )
        form_layout.addRow(
            "Horizontal flip dedup",
            self.allow_horizontal_flip_deduplication_check_box,
        )
        form_layout.addRow(
            "Vertical flip dedup",
            self.allow_vertical_flip_deduplication_check_box,
        )
        form_layout.addRow(
            "Lossy reduction",
            self.allow_lossy_reduction_check_box,
        )
        form_layout.addRow("Similarity metric", self.similarity_metric_combo_box)

        return group_box

    def _create_export_group_box(self) -> QGroupBox:
        """
        Create the export settings group.

        Returns:
            The configured group box.
        """
        group_box = QGroupBox("Export")
        form_layout = QFormLayout()
        group_box.setLayout(form_layout)

        self.output_name_line_edit = QLineEdit()

        self.export_preview_png_check_box = QCheckBox()
        self.export_tileset_png_check_box = QCheckBox()
        self.export_tilemap_csv_check_box = QCheckBox()
        self.export_palette_binary_check_box = QCheckBox()
        self.export_tiles_binary_check_box = QCheckBox()
        self.export_c_header_check_box = QCheckBox()

        form_layout.addRow("Output name", self.output_name_line_edit)
        form_layout.addRow("Preview PNG", self.export_preview_png_check_box)
        form_layout.addRow("Tileset PNG", self.export_tileset_png_check_box)
        form_layout.addRow("Tilemap CSV", self.export_tilemap_csv_check_box)
        form_layout.addRow("Palette binary", self.export_palette_binary_check_box)
        form_layout.addRow("Tiles binary", self.export_tiles_binary_check_box)
        form_layout.addRow("C header", self.export_c_header_check_box)

        return group_box

    def load_from_project_config(self, config: ProjectConfig) -> None:
        """
        Populate the UI controls from a ProjectConfig.

        Args:
            config: Project configuration to display.
        """
        if config is None:
            raise ValueError("config cannot be None.")

        self.palette_bank_count_spin_box.setValue(
            config.quantization.palette_bank_count
        )
        self.dithering_check_box.setChecked(config.quantization.dithering_enabled)
        self.pad_to_tile_grid_check_box.setChecked(config.quantization.pad_to_tile_grid)

        self.max_tiles_spin_box.setValue(config.tile_reduction.max_tiles)
        self.allow_exact_deduplication_check_box.setChecked(
            config.tile_reduction.allow_exact_deduplication
        )
        self.allow_horizontal_flip_deduplication_check_box.setChecked(
            config.tile_reduction.allow_horizontal_flip_deduplication
        )
        self.allow_vertical_flip_deduplication_check_box.setChecked(
            config.tile_reduction.allow_vertical_flip_deduplication
        )
        self.allow_lossy_reduction_check_box.setChecked(
            config.tile_reduction.allow_lossy_reduction
        )

        similarity_metric_index = self.similarity_metric_combo_box.findText(
            config.tile_reduction.similarity_metric
        )
        if similarity_metric_index >= 0:
            self.similarity_metric_combo_box.setCurrentIndex(similarity_metric_index)

        self.output_name_line_edit.setText(config.export.output_name)
        self.export_preview_png_check_box.setChecked(config.export.export_preview_png)
        self.export_tileset_png_check_box.setChecked(config.export.export_tileset_png)
        self.export_tilemap_csv_check_box.setChecked(config.export.export_tilemap_csv)
        self.export_palette_binary_check_box.setChecked(
            config.export.export_palette_binary
        )
        self.export_tiles_binary_check_box.setChecked(config.export.export_tiles_binary)
        self.export_c_header_check_box.setChecked(config.export.export_c_header)

    def build_project_config(self) -> ProjectConfig:
        """
        Build a ProjectConfig from the current UI values.

        Returns:
            A validated ProjectConfig instance.
        """
        config = ProjectConfig(
            quantization=QuantizationConfig(
                palette_bank_count=self.palette_bank_count_spin_box.value(),
                dithering_enabled=self.dithering_check_box.isChecked(),
                quantization_method="median_cut",
                tile_width=8,
                tile_height=8,
                pad_to_tile_grid=self.pad_to_tile_grid_check_box.isChecked(),
            ),
            tile_reduction=TileReductionConfig(
                max_tiles=self.max_tiles_spin_box.value(),
                allow_exact_deduplication=(
                    self.allow_exact_deduplication_check_box.isChecked()
                ),
                allow_horizontal_flip_deduplication=(
                    self.allow_horizontal_flip_deduplication_check_box.isChecked()
                ),
                allow_vertical_flip_deduplication=(
                    self.allow_vertical_flip_deduplication_check_box.isChecked()
                ),
                allow_lossy_reduction=(
                    self.allow_lossy_reduction_check_box.isChecked()
                ),
                similarity_metric=self.similarity_metric_combo_box.currentText(),
                error_threshold=0.0,
            ),
            export=ExportConfig(
                export_preview_png=self.export_preview_png_check_box.isChecked(),
                export_tileset_png=self.export_tileset_png_check_box.isChecked(),
                export_tilemap_csv=self.export_tilemap_csv_check_box.isChecked(),
                export_palette_binary=self.export_palette_binary_check_box.isChecked(),
                export_tiles_binary=self.export_tiles_binary_check_box.isChecked(),
                export_c_header=self.export_c_header_check_box.isChecked(),
                output_name=self.output_name_line_edit.text().strip(),
            ),
        )

        config.validate()
        return config
