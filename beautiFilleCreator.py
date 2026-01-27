import os
import sys
import json
import subprocess

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QFrame, QMessageBox, QPushButton,
    QWidget, QVBoxLayout, QFileDialog, QInputDialog
)
from PySide6.QtGui import QCursor, QIcon
from PySide6.QtCore import Qt, QSize, QFileInfo, QPropertyAnimation, QEasingCurve, QPoint, QEvent, QAbstractAnimation


CONFIG_FILE = "beautFile_config.json"


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

        # 2) Let user pick shortcuts (files/apps) for the group
        apps = []
        while True:
            path, _ = QFileDialog.getOpenFileName(
                self,
                "Select Application / Shortcut",
                "",
                "All Files (*.*)"
            )
            if not path:
                break

            file_info = QFileInfo(path)
            display_name = file_info.baseName() or file_info.fileName()
            apps.append((display_name, path))

            # Ask if they want to add another shortcut
            more = QMessageBox.question(
                self,
                "Add Another?",
                "Add another shortcut to this app group?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes,
            )
            if more != QMessageBox.Yes:
                break

        if not apps:
            QMessageBox.information(
                self,
                "No Shortcuts",
                "No shortcuts were added. App group was not created."
            )
            return

        # 3) Save group to config
        data = self.load_config()
        data[group_name] = apps
        self.save_config(data)

        QMessageBox.information(
            self,
            "App Group Created",
            f"App group '{group_name}' has been created."
        )

        # 4) Instantiate a BeautiFile window for this group
        self.launch_group(group_name)

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
