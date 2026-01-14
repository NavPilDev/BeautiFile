import sys
import subprocess
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFrame,
    QToolButton, QGridLayout, QFileIconProvider
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, QSize, QFileInfo
import win32com.client

APPS = [
    ("Valorant", r"C:\Riot Games\Riot Client\RiotClientServices.exe"),
    ("Steam", r"C:\Program Files (x86)\Steam\Steam.exe"),
    ("Epic Games", r"C:\Program Files (x86)\Epic Games\Launcher\Portal\Binaries\Win64\EpicGamesLauncher.exe"),
    ("Marvel Rivals", r"C:\Games\MarvelRivals.exe"),
]

class MainWindow(QWidget) :
    def __init__(self):
        super().__init__()
        
        icon_provider = QFileIconProvider()

        container = QFrame(self)
        container.setStyleSheet("""
        QFrame {
            background-color: rgba(36, 36, 36, 210);
        }
        """)
        layout = QGridLayout(container)
        layout.setContentsMargins(20, 20, 20, 20)
        
        for name, path in APPS:
            btn = QToolButton()
            btn.setText(name)

            file_info = QFileInfo(path)
            icon = icon_provider.icon(file_info)
            btn.setIcon(QIcon(icon))

            btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            btn.setIconSize(QSize(64, 64))
            
            btn.clicked.connect(lambda _, p = path: subprocess.Popen(p))
            layout.addWidget(btn)
        
        self.resize(container.sizeHint())
        container.resize(self.size())



app = QApplication(sys.argv)

window = MainWindow()
window.show()
app.exec()
