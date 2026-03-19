"""
Entry point for the GBA Tile Quantizer application.
Responsible only for bootstrapping the GUI application.
"""
from PySide6.QtWidgets import QApplication
import sys

from app.Application import Application


def main() -> None:
    """
    Application entry point.
    Initializes Qt and starts the main application.
    """

    qt_app = QApplication(sys.argv)
    application = Application(qt_app)
    application.run()
    sys.exit(qt_app.exec())


if __name__ == "__main__":
    main()
