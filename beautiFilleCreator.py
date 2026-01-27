import os
import sys
import json
import subprocess

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QFrame, QMessageBox, QPushButton,
    QWidget, QVBoxLayout, QFileDialog, QInputDialog, QLabel,
    QHBoxLayout, QToolButton, QFileIconProvider, QGridLayout
)
from PySide6.QtGui import QCursor, QIcon
from PySide6.QtCore import Qt, QSize, QFileInfo, QPropertyAnimation, QEasingCurve, QPoint, QEvent, QAbstractAnimation


CONFIG_FILE = "beautFile_config.json"


class AppGroupWindow(QMainWindow):
    """Small editor window that matches the Figma-style app group card."""

    def __init__(self, creator: "MainWindow", group_name: str):
        super().__init__(creator)
        self.creator = creator
        self.group_name = group_name
        self.apps = self.creator.load_config().get(group_name, [])
        self.icon_provider = QFileIconProvider()

        self.setWindowTitle(group_name)
        # Fix width to match design, allow height to grow with rows
        self.setFixedWidth(420)

        frame = QFrame()
        frame.setObjectName("appGroupFrame")
        self.setCentralWidget(frame)

        main_layout = QVBoxLayout(frame)
        main_layout.setContentsMargins(16, 12, 16, 12)
        main_layout.setSpacing(8)

        # Header
        header = QHBoxLayout()

        self.title_label = QLabel(self.group_name)
        self.title_label.setObjectName("appGroupTitle")
        header.addWidget(self.title_label)
        header.addStretch()

        self.settings_button = QToolButton()
        self.settings_button.setText("⚙")
        self.settings_button.setAutoRaise(True)

        self.close_button = QToolButton()
        self.close_button.setText("✕")
        self.close_button.setAutoRaise(True)
        self.close_button.clicked.connect(self.close)

        header.addWidget(self.settings_button)
        header.addWidget(self.close_button)

        main_layout.addLayout(header)

        # Center message + icons row
        self.empty_label = QLabel()
        self.empty_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.empty_label)

        self.icons_layout = QGridLayout()
        self.icons_layout.setHorizontalSpacing(24)
        self.icons_layout.setVerticalSpacing(16)
        main_layout.addLayout(self.icons_layout)

        # Import button row (centered at top like design)
        button_row = QHBoxLayout()
        button_row.addStretch()

        self.import_button = QPushButton("Import Files or Folder")
        self.import_button.clicked.connect(self.import_files)
        button_row.addWidget(self.import_button)

        button_row.addStretch()
        main_layout.insertLayout(1, button_row)

        # Styling
        frame.setStyleSheet(
            """
            QFrame#appGroupFrame {
                background-color: #2b2b2b;
                border-radius: 20px;
            }
            QLabel#appGroupTitle {
                color: #ffffff;
                font-weight: 600;
                text-decoration: underline;
            }
            QLabel {
                color: #e0e0e0;
            }
            QPushButton {
                background-color: #5a5a5a;
                color: white;
                border-radius: 8px;
                padding: 6px 14px;
            }
            QPushButton:hover {
                background-color: #707070;
            }
            """
        )

        self.update_empty_state()
        self.refresh_icons()

    def update_empty_state(self):
        if not self.apps:
            self.empty_label.setText("No files in app group!")
        else:
            self.empty_label.setText("")

    def refresh_icons(self):
        # Clear existing icon widgets
        while self.icons_layout.count():
            item = self.icons_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

        # Rebuild icons grid from self.apps, max 3 per row
        for index, (name, path) in enumerate(self.apps):
            row = index // 3
            grid_col = index % 3

            col_layout = QVBoxLayout()
            col_layout.setAlignment(Qt.AlignHCenter)

            icon_label = QLabel()
            file_info = QFileInfo(path)
            icon = self.icon_provider.icon(file_info)
            pix = icon.pixmap(QSize(48, 48))
            icon_label.setPixmap(pix)
            icon_label.setAlignment(Qt.AlignCenter)

            text_label = QLabel(name)
            text_label.setAlignment(Qt.AlignCenter)

            col_layout.addWidget(icon_label)
            col_layout.addWidget(text_label)

            wrapper = QWidget()
            wrapper.setLayout(col_layout)
            self.icons_layout.addWidget(wrapper, row, grid_col)

        # Let the window grow vertically as rows are added
        self.adjustSize()

    def import_files(self):
        # Single "Import" interaction; user can select multiple files at once
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Applications / Shortcuts",
            "",
            "All Files (*.*)"
        )
        if not paths:
            return

        for path in paths:
            file_info = QFileInfo(path)
            display_name = file_info.baseName() or file_info.fileName()
            self.apps.append((display_name, path))

        # Persist updates and launch the desktop bubble if we added anything
        if self.apps:
            data = self.creator.load_config()
            data[self.group_name] = self.apps
            self.creator.save_config(data)

            self.update_empty_state()
            self.refresh_icons()

            # Instantiate an app group on the home screen
            self.creator.launch_group(self.group_name)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        container = QWidget()
        self.setCentralWidget(container)
        self.setWindowTitle("BeautiFile Config")

        layout = QVBoxLayout(container)
        button = QPushButton("Create New App Group")
        button.clicked.connect(self.new_group_config)

        layout.addWidget(button)

    def load_config(self):
        if not os.path.exists(CONFIG_FILE):
            return {}
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception:
            # if the file is corrupt, start fresh
            return {}

    def save_config(self, data):
        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f, indent=4)

    def new_group_config(self):
        # 1) Ask for group name
        group_name, ok = QInputDialog.getText(
            self,
            "New App Group",
            "Enter a name for the new app group:",
        )
        if not ok or not group_name.strip():
            return
        group_name = group_name.strip()

        # Ensure group exists in config (possibly empty)
        data = self.load_config()
        data.setdefault(group_name, [])
        self.save_config(data)

        # 2) Open the Figma-style app group interface
        editor = AppGroupWindow(self, group_name)
        editor.show()

    def launch_group(self, group_name: str):
        """Launch a beautiFile window for the given group on the desktop."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(script_dir, "beautifile.py")

        if not os.path.exists(script_path):
            QMessageBox.warning(
                self,
                "Error",
                f"Could not find 'beautifile.py' at:\n{script_path}"
            )
            return

        try:
            subprocess.Popen([sys.executable, script_path, group_name])
        except Exception as e:
            QMessageBox.critical(
                self,
                "Launch Failed",
                f"Failed to launch app group '{group_name}':\n{e}"
            )


app = QApplication(sys.argv)

window = MainWindow()
window.show()
app.exec()
