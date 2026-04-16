"""
Palette display widget for the GBA Tile Quantizer.
"""
from __future__ import annotations

from typing import Optional

from PySide6.QtCore import QPoint, Qt, QRect
from PySide6.QtGui import QColor, QImage, QMouseEvent, QPainter, QPen, QPixmap, QWheelEvent
from PySide6.QtWidgets import QFrame, QGraphicsPixmapItem, QGraphicsScene, QGraphicsView, QVBoxLayout, QWidget

from domain.PaletteSet import PaletteSet


class _GraphicsPaletteView(QGraphicsView):
    """
    Internal graphics view supporting mouse-wheel zoom and click-drag pan.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)

        self._pixmap_item = QGraphicsPixmapItem()
        self._scene.addItem(self._pixmap_item)

        self._zoom_factor = 1.0
        self._zoom_step = 1.15
        self._min_zoom = 0.25
        self._max_zoom = 32.0

        self._is_panning = False
        self._last_mouse_position = QPoint()

        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setBackgroundBrush(Qt.GlobalColor.black)

    def set_pixmap(self, pixmap: QPixmap) -> None:
        """
        Display a pixmap in the view and reset the transform.
        """
        self._pixmap_item.setPixmap(pixmap)
        self._scene.setSceneRect(self._pixmap_item.boundingRect())
        self.reset_view()

    def clear_pixmap(self) -> None:
        """
        Remove the current pixmap from the view.
        """
        self._pixmap_item.setPixmap(QPixmap())
        self._scene.setSceneRect(self._pixmap_item.boundingRect())
        self.reset_view()

    def has_pixmap(self) -> bool:
        """
        Check whether a valid pixmap is currently loaded.
        """
        return not self._pixmap_item.pixmap().isNull()

    def reset_view(self) -> None:
        """
        Reset zoom and pan to default values and fit the pixmap in view.
        """
        self.resetTransform()
        self._zoom_factor = 1.0

        if self.has_pixmap():
            self.fitInView(
                self._pixmap_item,
                Qt.AspectRatioMode.KeepAspectRatio,
            )
            self._zoom_factor = self.transform().m11()

    def wheelEvent(self, event: QWheelEvent) -> None:
        """
        Zoom in or out with the mouse wheel.
        """
        if not self.has_pixmap():
            super().wheelEvent(event)
            return

        angle_delta = event.angleDelta().y()
        if angle_delta == 0:
            return

        scale_factor = self._zoom_step if angle_delta > 0 else 1.0 / self._zoom_step
        new_zoom = self._zoom_factor * scale_factor
        if new_zoom < self._min_zoom or new_zoom > self._max_zoom:
            return

        self.scale(scale_factor, scale_factor)
        self._zoom_factor = new_zoom

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """
        Start panning on left mouse button press.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_panning = True
            self._last_mouse_position = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """
        Pan the view while dragging the mouse.
        """
        if self._is_panning:
            delta = event.pos() - self._last_mouse_position
            self._last_mouse_position = event.pos()

            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - delta.x()
            )
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - delta.y()
            )

            event.accept()
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """
        Stop panning on left mouse button release.
        """
        if event.button() == Qt.MouseButton.LeftButton and self._is_panning:
            self._is_panning = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
            return

        super().mouseReleaseEvent(event)


class PaletteWidget(QWidget):
    """
    Widget used to display the 16 background palette banks as zoomable rows.
    """

    MAX_PALETTE_BANKS = 16

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.palette_set: Optional[PaletteSet] = None
        self.columns = 16
        self.rows = 1
        self.cell_size = 18
        self.cell_spacing = 4
        self.bank_spacing = 8
        self.bank_label_width = 44

        self.graphics_view = _GraphicsPaletteView(self)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.graphics_view)
        self.setLayout(layout)

        self._refresh_pixmap()

    def set_palette_set(self, palette_set: PaletteSet) -> None:
        """
        Set the palette banks to display.
        """
        self.palette_set = palette_set
        self._refresh_pixmap()

    def clear_palette(self) -> None:
        """
        Clear the displayed palette.
        """
        self.palette_set = None
        self._refresh_pixmap()

    def _refresh_pixmap(self) -> None:
        """
        Render the current palette banks into the graphics view.
        """
        pixmap = self._render_palette_pixmap()
        self.graphics_view.set_pixmap(pixmap)

    def _render_palette_pixmap(self) -> QPixmap:
        """
        Render all palette banks to a pixmap.
        """
        width = self._content_width()
        height = self._content_height()
        image = QImage(width, height, QImage.Format.Format_RGB32)
        image.fill(QColor(Qt.GlobalColor.black))

        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        painter.setPen(QPen(Qt.GlobalColor.gray))

        palette_banks = []
        if self.palette_set is not None:
            palette_banks = list(self.palette_set.palettes)

        for bank_index in range(self.MAX_PALETTE_BANKS):
            colors: list[tuple[int, int, int]] = []
            if bank_index < len(palette_banks):
                colors = list(palette_banks[bank_index].colors)

            while len(colors) < 16:
                colors.append((0, 0, 0))

            bank_y_offset = bank_index * (self._bank_height() + self.bank_spacing)
            label_rect = QRect(
                self.cell_spacing,
                bank_y_offset + self.cell_spacing,
                self.bank_label_width - self.cell_spacing,
                self.cell_size,
            )
            painter.setPen(QPen(Qt.GlobalColor.lightGray))
            painter.drawText(
                label_rect,
                int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft),
                f"Pal {bank_index}",
            )
            painter.setPen(QPen(Qt.GlobalColor.gray))

            for column in range(16):
                x = (
                    self.bank_label_width
                    + self.cell_spacing
                    + column * (self.cell_size + self.cell_spacing)
                )
                y = bank_y_offset + self.cell_spacing

                rect = QRect(x, y, self.cell_size, self.cell_size)
                red, green, blue = colors[column]
                painter.fillRect(rect, QColor(red, green, blue))
                painter.drawRect(rect)

        painter.end()
        return QPixmap.fromImage(image)

    def _bank_height(self) -> int:
        """
        Return the pixel height of a single palette bank row.
        """
        return (self.rows * self.cell_size) + ((self.rows + 1) * self.cell_spacing)

    def _content_width(self) -> int:
        """
        Return the rendered palette pixmap width.
        """
        return (
            self.bank_label_width
            + (self.columns * self.cell_size)
            + ((self.columns + 1) * self.cell_spacing)
        )

    def _content_height(self) -> int:
        """
        Return the rendered palette pixmap height.
        """
        return (self.MAX_PALETTE_BANKS * self._bank_height()) + (
            (self.MAX_PALETTE_BANKS - 1) * self.bank_spacing
        )
