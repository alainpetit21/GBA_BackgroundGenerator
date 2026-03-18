"""
Palette display widget for the GBA Tile Quantizer.
"""
from __future__ import annotations
from typing import Optional
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget

from domain.Palette import Palette


class PaletteWidget(QWidget):
    """
    Widget used to display a 16-color palette as a grid of swatches.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.palette: Optional[Palette] = None
        self.columns = 4
        self.rows = 4
        self.cell_size = 32
        self.cell_spacing = 6

        self.setMinimumSize(
            (self.columns * self.cell_size) + ((self.columns + 1) * self.cell_spacing),
            (self.rows * self.cell_size) + ((self.rows + 1) * self.cell_spacing),
        )

    def set_palette(self, palette: Palette) -> None:
        """
        Set the palette to display.

        Args:
            palette: Palette to display.
        """
        self.palette = palette
        self.update()

    def clear_palette(self) -> None:
        """
        Clear the displayed palette.
        """
        self.palette = None
        self.update()

    def paintEvent(self, event) -> None:
        """
        Paint the palette swatches.
        """
        super().paintEvent(event)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)

        painter.fillRect(self.rect(), Qt.GlobalColor.black)

        border_pen = QPen(Qt.GlobalColor.gray)
        painter.setPen(border_pen)

        colors = []
        if self.palette is not None:
            colors = list(self.palette.colors)

        while len(colors) < 16:
            colors.append((0, 0, 0))

        for index in range(16):
            row = index // self.columns
            column = index % self.columns

            x = self.cell_spacing + column * (self.cell_size + self.cell_spacing)
            y = self.cell_spacing + row * (self.cell_size + self.cell_spacing)

            rect = QRect(x, y, self.cell_size, self.cell_size)

            red, green, blue = colors[index]
            painter.fillRect(rect, QColor(red, green, blue))
            painter.drawRect(rect)

        painter.end()
