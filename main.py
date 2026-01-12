from PySide6.QtWidgets import QApplication, QCheckBox, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLineEdit, QTextEdit, QSlider, QProgressBar, QComboBox, QListWidget, QRadioButton # Used for application, main window of application, and label
from PySide6.QtCore import Qt # Styling



class MainWindow(QMainWindow) :

    def __init__(self): #runs automically when object of class is created
        super().__init__()

        self.setWindowTitle('Hello World Application')

        container = QWidget()
        self.setCentralWidget(container)

        layout = QVBoxLayout(container)

        label = QLabel('Label');
        label.setAlignment(Qt.AlignCenter)

        button = QPushButton('Click Me')
        line_edit = QLineEdit()
        text_edit = QTextEdit()

        combobox = QComboBox()
        combobox.addItems(['One', 'Two', 'Three'])

        listWidget = QListWidget();
        listWidget.addItems(['One', 'Two', 'Three'])

        # containers + check boxes
        inner_container = QWidget()

        inner_layout = QHBoxLayout(inner_container)

        checkBox1 = QCheckBox('One')
        checkBox2 = QCheckBox('Two')
        checkBox3 = QCheckBox('Three')

        inner_layout.addWidget(checkBox1)
        inner_layout.addWidget(checkBox2)
        inner_layout.addWidget(checkBox3)

        layout.addWidget(label)
        layout.addWidget(button)
        layout.addWidget(line_edit)
        layout.addWidget(text_edit)
        layout.addWidget(combobox)
        layout.addWidget(listWidget)
        layout.addWidget(inner_container)



app = QApplication() # Must exist first to instantiate app

window = MainWindow() # Registers with active QApplication instance
window.show() # Show window on app

app.exec() # Starts the event loop. Events include widgets such as MainWindow