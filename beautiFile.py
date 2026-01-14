import sys
import subprocess
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFrame,
    QToolButton, QGridLayout, QFileIconProvider
)
from PySide6.QtGui import QCursor, QIcon
from PySide6.QtCore import Qt, QSize, QFileInfo

APPS = [
    ("Valorant", r"C:\Riot Games\Riot Client\RiotClientServices.exe"),
    ("Steam", r"C:\Program Files (x86)\Steam\Steam.exe"),
    ("Epic Games", r"C:\Program Files (x86)\Epic Games\Launcher\Portal\Binaries\Win64\EpicGamesLauncher.exe"),
    ("Marvel Rivals", r"C:\Games\MarvelRivals.exe"),
]

class MainWindow(QWidget) :
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.Tool |
            Qt.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        icon_provider = QFileIconProvider()

        container = QFrame(self)
        container.setStyleSheet("""
        QFrame {
            background-color: rgba(36, 36, 36, 210);
            border-radius: 20px;
        }
        """)

        layout = QGridLayout(container)
        layout.setContentsMargins(20, 20, 20, 20)
        
        for i, (name, path) in enumerate(APPS):
            btn = QToolButton()
            btn.setText(name)

            file_info = QFileInfo(path)
            icon = icon_provider.icon(file_info)
            btn.setIcon(QIcon(icon))

            btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            btn.setIconSize(QSize(64, 64))
            
            btn.clicked.connect(lambda _, p=path: self.shortCutClicked(p))
            layout.addWidget(btn, 0, i)
        
        self.resize(container.sizeHint())
        container.resize(self.size())

        cursor_pos = QCursor.pos()
        screen_geom = QApplication.primaryScreen().availableGeometry()

        x = cursor_pos.x() + 60
        y = cursor_pos.y() - self.height() // 2 

        self.move(x,y)

    def focusOutEvent(self, event):
        self.close()
        super().focusOutEvent(event)
    
    def keyPressEvent(self, event):
        key = event.key()
        print(event.text())
        if event.key() == Qt.Key_Escape:
            self.close()

    def closeEvent(self, event):
        QApplication.quit()
    
    def shortCutClicked(self, path):
        subprocess.Popen(path)
        self.close()


app = QApplication(sys.argv)

window = MainWindow()
window.show()
app.exec()
