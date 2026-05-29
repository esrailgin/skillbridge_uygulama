import sys
from pathlib import Path

from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QApplication

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from desktop.config import STYLE
from desktop.screens.main_window import AnaPencere


def _apply_light_palette(app: QApplication):
    palette = app.palette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#F4F6F8"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#1F2937"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#FFFFFF"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#F8FAFC"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#1F2937"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#FFFFFF"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#1F2937"))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#111827"))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#F9FAFB"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#DDF7F4"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#0F3D3A"))
    app.setPalette(palette)
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    _apply_light_palette(app)
    app.setStyleSheet(STYLE)
    pencere = AnaPencere()
    pencere.show()
    sys.exit(app.exec())

