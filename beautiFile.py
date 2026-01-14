import sys
import subprocess
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFrame,
    QToolButton, QGridLayout, QFileIconProvider
)
from PySide6.QtGui import QCursor, QIcon
from PySide6.QtCore import Qt, QSize, QFileInfo, QPropertyAnimation, QEasingCurve, QPoint, QEvent, QAbstractAnimation

APPS = [
    ("Valorant", r"C:\Riot Games\Riot Client\RiotClientServices.exe"),
    ("Steam", r"C:\Program Files (x86)\Steam\Steam.exe"),
    ("Epic Games", r"C:\Program Files (x86)\Epic Games\Launcher\Portal\Binaries\Win64\EpicGamesLauncher.exe"),
    ("Marvel Rivals", r"C:\Games\MarvelRivals.exe"),
]

class MainWindow(QWidget) :
    def __init__(self):
        super().__init__()
        QApplication.instance().installEventFilter(self)

        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.Tool |
            Qt.WindowStaysOnTopHint |
            Qt.Popup
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
        layout.setContentsMargins(10, 10, 10, 10)
        
        for i, (name, path) in enumerate(APPS):
            btn = QToolButton()
            btn.setText(name)

            file_info = QFileInfo(path)
            icon = icon_provider.icon(file_info)
            btn.setIcon(QIcon(icon))

            btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            btn.setIconSize(QSize(48, 48))
            
            btn.clicked.connect(lambda _, p=path: self.shortCutClicked(p))
            layout.addWidget(btn, 0, i)
        
        self.resize(container.sizeHint())
        container.resize(self.size())

        screen = QApplication.primaryScreen()
        geom = screen.availableGeometry()

        # Approximate desktop icon grid cell size (tweak these to match your setup)
        cell_w = 100   # width of one desktop icon slot
        cell_h = 102   # height of one desktop icon slot

        cursor = QCursor.pos()

        # Convert cursor pos to grid coordinates (relative to desktop top-left)
        col = (cursor.x() - geom.left()) // cell_w
        row = (cursor.y() - geom.top())  // cell_h

        # Target cell: one cell to the right
        target_col = col + 2

        # Top-left of that target cell
        target_x = geom.left() + target_col * cell_w
        target_y = geom.top()  + row       * cell_h

        # Center our window inside that cell
        x = int(target_x + (cell_w - self.width()) / 2)
        y = int(target_y + (cell_h - self.height()) / 2)

        # Clamp to screen
        x = max(geom.left(), min(x, geom.right() - self.width()))
        y = max(geom.top(),  min(y, geom.bottom() - self.height()))

        self.move(x, y)

        ########## Animations ############
        self.setWindowOpacity(0.0)
        self._start_pos = self.pos()
        
        self.opacity_anim = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_anim.setDuration(200)
        self.opacity_anim.setStartValue(0.0)
        self.opacity_anim.setEndValue(1.0)
        self.opacity_anim.setEasingCurve(QEasingCurve.OutCubic)

        self.pos_anim = QPropertyAnimation(self, b"pos")
        self.pos_anim.setDuration(200)
        self.pos_anim.setStartValue(self._start_pos + QPoint(-20, 0))  # 20px to the left
        self.pos_anim.setEndValue(self._start_pos)
        self.pos_anim.setEasingCurve(QEasingCurve.OutCubic)

        self._closing = False

    def showEvent(self, event):
        super().showEvent(event)

        self.activateWindow()
        self.raise_()
        self.setFocus()

        # restart animations each time it shows
        self.opacity_anim.start()
        self.pos_anim.start()

    def close_with_animation(self):
        if self._closing:
            return
        self._closing = True

        self.opacity_anim.setDirection(QAbstractAnimation.Backward)
        self.pos_anim.setDirection(QAbstractAnimation.Backward)

        self.opacity_anim.finished.connect(QApplication.quit)

        self.opacity_anim.start()
        self.pos_anim.start()

    def focusOutEvent(self, event):
        self.close_with_animation()
        super().focusOutEvent(event)
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close_with_animation()

    def closeEvent(self, event):
        QApplication.quit()
    
    def shortCutClicked(self, path):
        subprocess.Popen(path)
        self.close_with_animation()

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress and self.isVisible():
            # global mouse position
            pos = event.globalPos()
            # if click is outside this window, close it
            if not self.geometry().contains(pos):
                self.close_with_animation()
        return super().eventFilter(obj, event)


app = QApplication(sys.argv)

window = MainWindow()
window.show()
app.exec()
