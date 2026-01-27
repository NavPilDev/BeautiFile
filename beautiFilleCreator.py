import os
import sys
import json
import subprocess

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QFrame, QMessageBox, QPushButton,
    QWidget, QVBoxLayout, QFileDialog, QInputDialog, QLabel,
    QHBoxLayout, QToolButton, QFileIconProvider, QGridLayout, QLineEdit
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
        self.setWindowTitle("BeautiFile")

        self.group_windows = []

        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)

        # Top bar: search + controls
        top_bar = QHBoxLayout()

        # Search field styled like Figma
        search_frame = QFrame()
        search_frame.setObjectName("searchFrame")
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(8, 4, 8, 4)
        search_layout.setSpacing(6)

        search_icon = QLabel("🔍")
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search for an App Group...")
        self.search_edit.textChanged.connect(self.refresh_groups)

        search_layout.addWidget(search_icon)
        search_layout.addWidget(self.search_edit)

        top_bar.addWidget(search_frame, 1)

        # Spacer then plus/settings/close controls
        add_button = QToolButton()
        add_button.setText("+")
        add_button.setAutoRaise(True)
        add_button.clicked.connect(self.new_group_config)

        settings_button = QToolButton()
        settings_button.setText("⚙")
        settings_button.setAutoRaise(True)

        close_button = QToolButton()
        close_button.setText("✕")
        close_button.setAutoRaise(True)
        close_button.clicked.connect(self.close)

        top_bar.addSpacing(8)
        top_bar.addWidget(add_button)
        top_bar.addWidget(settings_button)
        top_bar.addWidget(close_button)

        layout.addLayout(top_bar)

        # Center content: empty state or group tiles
        center = QVBoxLayout()
        center.setAlignment(Qt.AlignCenter)

        self.empty_label = QLabel("No beautiFiles created!")
        self.empty_label.setAlignment(Qt.AlignCenter)

        self.create_group_button = QPushButton("Create New App Group")
        self.create_group_button.clicked.connect(self.new_group_config)

        center.addWidget(self.empty_label)
        center.addWidget(self.create_group_button)

        layout.addLayout(center)

        # Grid of group cards (shown when there are groups)
        self.groups_layout = QGridLayout()
        self.groups_layout.setHorizontalSpacing(24)
        self.groups_layout.setVerticalSpacing(16)
        layout.addLayout(self.groups_layout)

        # Styling for search and main container
        container.setStyleSheet(
            """
            QFrame#searchFrame {
                background-color: #5a5a5a;
                border-radius: 10px;
            }
            QLineEdit {
                border: none;
                background: transparent;
                color: white;
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

        self.refresh_groups()

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
        # whenever config changes, refresh list
        self.refresh_groups()

    def clear_group_tiles(self):
        while self.groups_layout.count():
            item = self.groups_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

    def refresh_groups(self):
        """Refresh the main screen list of app groups from config."""
        data = self.load_config()
        query = self.search_edit.text().strip().lower() if hasattr(self, "search_edit") else ""

        # Filter by search
        groups = [
            (name, apps)
            for name, apps in data.items()
            if not query or query in name.lower()
        ]

        self.clear_group_tiles()

        if not groups:
            # Show empty state
            self.empty_label.show()
            self.create_group_button.show()
            return

        self.empty_label.hide()
        self.create_group_button.hide()

        icon_provider = QFileIconProvider()

        for index, (group_name, apps) in enumerate(groups):
            row = index // 3
            col = index % 3

            # Outer clickable card (no heavy background)
            card = QFrame()
            card.setObjectName("groupCard")
            card_layout = QHBoxLayout(card)
            card_layout.setContentsMargins(4, 4, 4, 4)
            card_layout.setSpacing(8)

            # Thumbnail rounded square
            thumb = QFrame()
            thumb.setObjectName("groupThumb")
            thumb.setFixedSize(70, 70)
            thumb_layout = QHBoxLayout(thumb)
            thumb_layout.setContentsMargins(8, 8, 8, 8)
            thumb_layout.setSpacing(4)

            # Small icon strip inside thumbnail (up to 3 icons, then ...)
            for i, (_, path) in enumerate(apps[:3]):
                icon_label = QLabel()
                file_info = QFileInfo(path)
                icon = icon_provider.icon(file_info)
                pix = icon.pixmap(QSize(24, 24))
                icon_label.setPixmap(pix)
                thumb_layout.addWidget(icon_label)

            if len(apps) > 3:
                more_label = QLabel("…")
                thumb_layout.addWidget(more_label)

            card_layout.addWidget(thumb)

            # Text column
            text_col = QVBoxLayout()
            text_col.setContentsMargins(0, 0, 0, 0)
            text_col.setSpacing(2)

            name_label = QLabel(group_name)
            name_label.setObjectName("groupName")
            count = len(apps)
            files_label = QLabel(f"{count} file" + ("" if count == 1 else "s"))

            text_col.addWidget(name_label)
            text_col.addWidget(files_label)

            card_layout.addLayout(text_col)

            # Styling for thumbnail and name
            card.setStyleSheet(
                """
                QFrame#groupThumb {
                    background-color: #555359;
                    border-radius: 18px;
                }
                QLabel#groupName {
                    color: white;
                    font-weight: 600;
                }
                """
            )

            # Clicking a card opens the AppGroupWindow
            def make_open(name):
                def handler(event):
                    self.open_group(name)
                return handler

            card.mousePressEvent = make_open(group_name)

            self.groups_layout.addWidget(card, row, col)

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
        self.open_group(group_name)

    def open_group(self, group_name: str):
        editor = AppGroupWindow(self, group_name)
        self.group_windows.append(editor)
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
