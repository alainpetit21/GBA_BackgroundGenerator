"""
Application bootstrap layer for the GBA Tile Quantizer.
Responsible for creating the controller and main window,
wiring them together, and starting the UI.
"""
from PySide6.QtWidgets import QApplication

from app.Controller import Controller
from gui.MainWindow import MainWindow


class Application:
    """
    Coordinates top-level application startup.
    """

    def __init__(self, qt_app: QApplication) -> None:
        """
        Initialize the application bootstrap layer.

        Args:
            qt_app: The Qt application instance.
        """
        self.qt_app = qt_app
        self.controller = Controller()
        self.main_window = MainWindow(self.controller)

    def run(self) -> None:
        """
        Start the application UI.
        """
        self.main_window.show()
