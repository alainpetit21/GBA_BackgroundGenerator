"""
Zoomable and pannable image preview widget for the GBA Tile Quantizer.
"""
from __future__ import annotations
from typing import Optional
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QPixmap, QWheelEvent, QMouseEvent
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsPixmapItem,
    QGraphicsScene,
    QGraphicsView,
    QVBoxLayout,
    QWidget,
)


class _GraphicsImageView(QGraphicsView):
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
        self._min_zoom = 0.1
        self._max_zoom = 64.0

        self._is_panning = False
        self._last_mouse_position = QPoint()

        self.setRenderHints(self.renderHints())
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

        Args:
            pixmap: Pixmap to display.
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

        Returns:
            True if a pixmap is present, otherwise False.
        """
        return not self._pixmap_item.pixmap().isNull()

    def reset_view(self) -> None:
        """
        Reset zoom and pan to default values and fit the image in view.
        """
        self.resetTransform()
        self._zoom_factor = 1.0

        if self.has_pixmap():
            self.fitInView(
                self._pixmap_item,
                Qt.AspectRatioMode.KeepAspectRatio,
            )
            current_transform = self.transform()
            self._zoom_factor = current_transform.m11()

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

        if angle_delta > 0:
            scale_factor = self._zoom_step
        else:
            scale_factor = 1.0 / self._zoom_step

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


class ImagePreviewWidget(QWidget):
    """
    Public widget used to preview images with zoom and pan support.
    """

    def __init__(self, placeholder_text: str, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.placeholder_text = placeholder_text
        self.graphics_view = _GraphicsImageView(self)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.graphics_view)
        self.setLayout(layout)

    def set_pixmap(self, pixmap: QPixmap) -> None:
        """
        Set the displayed pixmap.

        Args:
            pixmap: Pixmap to display.
        """
        self.graphics_view.set_pixmap(pixmap)

    def clear_pixmap(self) -> None:
        """
        Clear the displayed pixmap.
        """
        self.graphics_view.clear_pixmap()

    def reset_view(self) -> None:
        """
        Reset zoom and pan.
        """
        self.graphics_view.reset_view()
