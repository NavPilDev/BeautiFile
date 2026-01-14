from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QMessageBox, QLabel # Used for application, main window of application, and label
from PySide6.QtCore import Qt # Styling

class SecondaryWindow(QMainWindow) :
    def __init__(self, n):
        super().__init__()
        self.setWindowTitle(f'Window number {n}')

        label = QLabel(f'Number {n}')
        label.setAlignment(Qt.AlignCenter)

class MainWindow(QMainWindow) :

    def __init__(self): #runs automically when object of class is created
        super().__init__()
        button = QPushButton("Open secondary window")
        button.clicked.connect(self.open_window)

        self.setCentralWidget(button)

        self.count = 1
        self.windows = []

    def open_window(self):
        w = SecondaryWindow(self.count)
        
        self.count += 1
        self.windows.append(w)
        w.show()



#%% | MessageBoxes and Choices/Dialogues
    #     self.setWindowTitle('Hello World Application')
        
    #     button = QPushButton('Show Choices')
    #     button.clicked.connect(self.ask_choices)


    #     self.setCentralWidget(button)

    # def ask_choices(self):
    #     msg = QMessageBox(self)

    #     msg.setWindowTitle('Choice')
    #     msg.setText("Select your favorite programming language")
    #     python = msg.addButton('Python', QMessageBox.AcceptRole)
    #     cpp = msg.addButton('C++', QMessageBox.AcceptRole)
    #     java = msg.addButton('Java', QMessageBox.AcceptRole)

    #     msg.exec()

    #     if msg.clickedButton() == python:
    #         print("User's favorite programming language is Python")
    #     elif msg.clickedButton() == cpp:
    #         print("User's favorite programming language is C++")
    #     else: 
    #         print("User's favorite programming language is Java")
    #     # if QMessageBox.question(self, 'Question', 'Do you like python?') == QMessageBox.Yes:
    #     #     print("User likes python")
    #     # else:
    #     #     print("User does not like python")
#%%

        

#%% | Menus, Submenus, and Actions
        # menuBar = self.menuBar();
        # fileMenu = menuBar.addMenu('File')
        # editMenu = menuBar.addMenu('Home')
        # helpMenu = menuBar.addMenu('?')

        # subMenu = fileMenu.addMenu('Submenu')

        # exitAction = subMenu.addAction('Exit')
        # aboutAction = helpMenu.addAction('About')

        # exitAction.triggered.connect(self.close)
        # aboutAction.triggered.connect(lambda: print(f"This is a tutorial GUI app!"))
#%%

#%% | Components and Layouts |
        # container = QWidget()
        # self.setCentralWidget(container)

    #     layout = QVBoxLayout(container)

    #     label = QLabel('Label');
    #     label.setAlignment(Qt.AlignCenter)

    #     button = QPushButton('Click Me')
    #     button.clicked.connect(lambda: print('Button Clicked!'))

    #     listWidget = QListWidget();
    #     listWidget.addItems(['One', 'Two', 'Three'])

    #     listWidget.itemClicked.connect(lambda item: print(f'Item Clicked {item.text()}'))
    #     listWidget.itemDoubleClicked.connect(lambda item: print(f'Item Clicked {item.text()}'))

    #     # containers + check boxes
    #     inner_container = QWidget()

    #     inner_layout = QHBoxLayout(inner_container)

    #     radio1 = QRadioButton('One')
    #     radio2 = QRadioButton('Two')
    #     radio3 = QRadioButton('Three')

    #     for r in (radio1, radio2, radio3):
    #         r.toggled.connect(self.radio_changed)

    #     inner_layout.addWidget(radio1)
    #     inner_layout.addWidget(radio2)
    #     inner_layout.addWidget(radio3)


    #     layout.addWidget(label)
    #     layout.addWidget(button)
    #     layout.addWidget(listWidget)
    #     layout.addWidget(inner_container)
        

    # def radio_changed(self): 
    #     r = self.sender()
    #     if r.isChecked():
    #         print("Radio button was selected! Value", r.text())
#%%

app = QApplication() # Must exist first to instantiate app

window = MainWindow() # Registers with active QApplication instance
window.show() # Show window on app

app.exec() # Starts the event loop. Events include widgets such as MainWindow