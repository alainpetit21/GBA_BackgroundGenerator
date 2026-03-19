"""
Main application window for the GBA Tile Quantizer.
"""
from __future__ import annotations
from pathlib import Path
from typing import Optional
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QPixmap
from PySide6.QtWidgets import QFileDialog, QMainWindow, QMessageBox, QPushButton, QSplitter, QTextEdit, QToolBar, \
    QVBoxLayout, QWidget, QHBoxLayout, QGroupBox

from app.Controller import Controller
from gui.widgets.ImagePreviewWidget import ImagePreviewWidget
from gui.widgets.ConfigPanelWidget import ConfigPanelWidget
from gui.widgets.PaletteWidget import PaletteWidget


class MainWindow(QMainWindow):
    """
    Main window of the GBA Tile Quantizer application.
    """

    def __init__(self, controller: Controller) -> None:
        super().__init__()

        self.controller = controller

        self.setWindowTitle("GBA Tile Quantizer")
        self.resize(1400, 850)

        self.config_panel_widget: Optional[ConfigPanelWidget] = None
        self.original_image_widget: Optional[ImagePreviewWidget] = None
        self.quantized_preview_widget: Optional[ImagePreviewWidget] = None
        self.tileset_preview_widget: Optional[ImagePreviewWidget] = None
        self.palette_widget: Optional[PaletteWidget] = None
        self.log_text_edit: Optional[QTextEdit] = None
        self.load_button: Optional[QPushButton] = None
        self.process_button: Optional[QPushButton] = None
        self.export_button: Optional[QPushButton] = None

        self._build_ui()
        self._refresh_ui_state()

    def _build_ui(self) -> None:
        self._create_actions()
        self._create_menu_bar()
        self._create_tool_bar()
        self._create_central_widget()

    def _create_actions(self) -> None:
        self.load_image_action = QAction("Load Image...", self)
        self.load_image_action.triggered.connect(self._on_load_image_clicked)

        self.process_image_action = QAction("Process", self)
        self.process_image_action.triggered.connect(self._on_process_clicked)

        self.export_action = QAction("Export...", self)
        self.export_action.triggered.connect(self._on_export_clicked)

        self.exit_action = QAction("Exit", self)
        self.exit_action.triggered.connect(self.close)

        self.about_action = QAction("About", self)
        self.about_action.triggered.connect(self._on_about_clicked)

    def _create_menu_bar(self) -> None:
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("File")
        file_menu.addAction(self.load_image_action)
        file_menu.addAction(self.process_image_action)
        file_menu.addAction(self.export_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)

        help_menu = menu_bar.addMenu("Help")
        help_menu.addAction(self.about_action)

    def _create_tool_bar(self) -> None:
        tool_bar = QToolBar("Main Toolbar", self)
        tool_bar.setMovable(False)

        tool_bar.addAction(self.load_image_action)
        tool_bar.addAction(self.process_image_action)
        tool_bar.addAction(self.export_action)

        self.addToolBar(tool_bar)

    def _create_central_widget(self) -> None:
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        top_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(top_splitter, stretch=1)

        preview_panel = self._create_preview_panel()
        right_panel = self._create_right_panel()

        top_splitter.addWidget(preview_panel)
        top_splitter.addWidget(right_panel)
        top_splitter.setSizes([1000, 400])

        button_row = self._create_button_row()
        main_layout.addLayout(button_row)

    def _create_preview_panel(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout()
        container.setLayout(layout)

        top_row = QHBoxLayout()
        layout.addLayout(top_row, stretch=1)

        self.original_image_widget = ImagePreviewWidget("Original Image")
        self.quantized_preview_widget = ImagePreviewWidget("Quantized Preview")

        right_column = QVBoxLayout()

        self.tileset_preview_widget = ImagePreviewWidget("Tileset Preview")
        self.palette_widget = PaletteWidget()

        right_column.addWidget(
            self._wrap_in_group_box("Tileset", self.tileset_preview_widget),
            stretch=1,
        )
        right_column.addWidget(
            self._wrap_in_group_box("Palette", self.palette_widget),
            stretch=0,
        )

        top_row.addWidget(
            self._wrap_in_group_box("Original", self.original_image_widget),
            stretch=1,
        )
        top_row.addWidget(
            self._wrap_in_group_box("Quantized", self.quantized_preview_widget),
            stretch=1,
        )

        right_column_container = QWidget()
        right_column_container.setLayout(right_column)
        top_row.addWidget(right_column_container, stretch=1)

        return container

    def _create_right_panel(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout()
        container.setLayout(layout)

        self.config_panel_widget = ConfigPanelWidget()
        self.config_panel_widget.load_from_project_config(self.controller.project_config)

        layout.addWidget(
            self._wrap_in_group_box("Configuration", self.config_panel_widget),
            stretch=1,
        )

        self.log_text_edit = QTextEdit()
        self.log_text_edit.setReadOnly(True)

        layout.addWidget(
            self._wrap_in_group_box("Log", self.log_text_edit),
            stretch=1,
        )

        return container

    def _create_button_row(self) -> QHBoxLayout:
        layout = QHBoxLayout()

        self.load_button = QPushButton("Load Image...")
        self.load_button.clicked.connect(self._on_load_image_clicked)

        self.process_button = QPushButton("Process")
        self.process_button.clicked.connect(self._on_process_clicked)

        self.export_button = QPushButton("Export...")
        self.export_button.clicked.connect(self._on_export_clicked)

        layout.addWidget(self.load_button)
        layout.addWidget(self.process_button)
        layout.addWidget(self.export_button)
        layout.addStretch()

        return layout

    def _wrap_in_group_box(self, title: str, widget: QWidget) -> QGroupBox:
        group_box = QGroupBox(title)
        layout = QVBoxLayout()
        layout.addWidget(widget)
        group_box.setLayout(layout)
        return group_box

    def _on_load_image_clicked(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image",
            "",
            "Images (*.png *.bmp *.jpg *.jpeg *.gif)",
        )

        if not file_path:
            return

        try:
            message = self.controller.load_image(file_path)
            self._log(message)

            self._set_preview_from_file(
                self.original_image_widget,
                Path(file_path),
            )

            self._clear_processed_previews()
            self._refresh_ui_state()
        except Exception as exception:  # noqa: BLE001
            self._show_error("Load Image Error", str(exception))

    def _on_process_clicked(self) -> None:
        try:
            self._apply_config_from_ui()

            message = self.controller.process_image()
            self._log(message)

            result = self.controller.get_current_result()
            if result is not None:
                self._set_preview_from_png_bytes(
                    self.quantized_preview_widget,
                    result.preview_image_bytes,
                )
                self._set_preview_from_png_bytes(
                    self.tileset_preview_widget,
                    result.tileset_preview_image_bytes,
                )
                if self.palette_widget is not None:
                    self.palette_widget.set_palette(result.palette)

            self._refresh_ui_state()
        except Exception as exception:  # noqa: BLE001
            self._show_error("Process Error", str(exception))

    def _on_export_clicked(self) -> None:
        output_directory = QFileDialog.getExistingDirectory(
            self,
            "Select Export Directory",
            "",
        )

        if not output_directory:
            return

        try:
            self._apply_config_from_ui()

            message = self.controller.export_result(output_directory)
            self._log(message)
        except Exception as exception:  # noqa: BLE001
            self._show_error("Export Error", str(exception))

    def _on_about_clicked(self) -> None:
        QMessageBox.information(
            self,
            "About GBA Tile Quantizer",
            (
                "GBA Tile Quantizer\n\n"
                "Version 1 prototype\n"
                "Mouse wheel: zoom\n"
                "Left-click drag: pan"
            ),
        )

    def _clear_processed_previews(self) -> None:
        if self.quantized_preview_widget is not None:
            self.quantized_preview_widget.clear_pixmap()

        if self.tileset_preview_widget is not None:
            self.tileset_preview_widget.clear_pixmap()

        if self.palette_widget is not None:
            self.palette_widget.clear_palette()

    def _set_preview_from_file(
        self,
        preview_widget: Optional[ImagePreviewWidget],
        image_path: Path,
    ) -> None:
        if preview_widget is None:
            return

        pixmap = QPixmap(str(image_path))
        if pixmap.isNull():
            raise ValueError(f"Failed to load image into preview: {image_path}")

        preview_widget.set_pixmap(pixmap)

    def _set_preview_from_png_bytes(
        self,
        preview_widget: Optional[ImagePreviewWidget],
        png_bytes: Optional[bytes],
    ) -> None:
        if preview_widget is None or not png_bytes:
            return

        pixmap = QPixmap()
        if not pixmap.loadFromData(png_bytes):
            raise ValueError("Failed to load preview image from PNG bytes.")

        preview_widget.set_pixmap(pixmap)

    def _refresh_ui_state(self) -> None:
        has_loaded_image = self.controller.has_loaded_image()
        has_result = self.controller.has_result()

        self.process_image_action.setEnabled(has_loaded_image)
        self.export_action.setEnabled(has_result)

        if self.process_button is not None:
            self.process_button.setEnabled(has_loaded_image)

        if self.export_button is not None:
            self.export_button.setEnabled(has_result)

    def _log(self, message: str) -> None:
        if self.log_text_edit is None:
            return

        self.log_text_edit.append(message)

    def _show_error(self, title: str, message: str) -> None:
        self._log(f"ERROR: {message}")
        QMessageBox.critical(self, title, message)

    def _apply_config_from_ui(self) -> None:
        """
        Read the current configuration panel values and apply them to the controller.
        """
        if self.config_panel_widget is None:
            return

        config = self.config_panel_widget.build_project_config()
        self.controller.set_project_config(config)