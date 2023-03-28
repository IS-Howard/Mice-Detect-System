
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QGridLayout, QLineEdit, QPushButton, QFileDialog, QHBoxLayout, QWidget, QListWidget, QVBoxLayout
from datetime import datetime

class Loader(object):
    # def __init__(self):
    #     super().__init__()
    #     self.initUI()
    #     self.resize(800, 300)

    def initUI(self, Dialog):
        Dialog.setWindowTitle('Data Loader')
        Dialog.resize(800,300)

        # Name
        self.name_label = QLabel('Name:')
        self.name_edit = QLineEdit()

        # Gender
        self.gender_label = QLabel('Gender:')
        self.gender_edit = QLineEdit()

        # Birthday
        self.birthday_label = QLabel('Birthday (dd/mm/yyyy):')
        self.birthday_edit = QLineEdit()

        # Age
        self.age_label = QLabel('Age (weeks):')
        self.age_edit = QLineEdit()

        # File
        self.file_label = QLabel('File:')
        self.file_edit = QLineEdit()
        self.file_button = QPushButton('Browse')
        self.file_button.clicked.connect(self.openFileDialog)

        # Create Object Button
        self.create_button = QPushButton('Create Object')
        self.create_button.clicked.connect(self.createObject)

        # list area
        self.list_widget = QListWidget()

        # Grid Layout
        grid = QGridLayout()
        grid.addWidget(self.name_label, 0, 0)
        grid.addWidget(self.name_edit, 0, 1)
        grid.addWidget(self.gender_label, 1, 0)
        grid.addWidget(self.gender_edit, 1, 1)
        grid.addWidget(self.birthday_label, 2, 0)
        grid.addWidget(self.birthday_edit, 2, 1)
        grid.addWidget(self.age_label, 3, 0)
        grid.addWidget(self.age_edit, 3, 1)
        grid.addWidget(self.file_label, 4, 0)
        grid.addWidget(self.file_edit, 4, 1)
        grid.addWidget(self.file_button, 4, 2)
        grid.addWidget(self.create_button, 5, 1)

        # Central Widget
        central_widget = QWidget()
        hbox = QHBoxLayout()
        hbox.addLayout(grid)
        hbox.addWidget(self.list_widget)
        # central_widget.setLayout(hbox)
        # self.setLayout(central_widget)

        # Set central widget
        Dialog.setLayout(hbox)

    def openFileDialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File")
        self.file_edit.setText(file_path)

    def createObject(self):
        name = self.name_edit.text()
        gender = self.gender_edit.text()
        birthday = datetime.strptime(self.birthday_edit.text(), '%d/%m/%Y')
        age = int(self.age_edit.text())
        file_path = self.file_edit.text()

        # Do something with the object properties (e.g., create a new object)