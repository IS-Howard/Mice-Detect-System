# from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QGridLayout, QPushButton, QWidget

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(400, 400)
        self.pushButton = QPushButton()
        self.pushButton.setText("Load Videos")
        self.pushButton.setFixedSize(160, 80)
        self.pushButton_2 = QPushButton()
        self.pushButton_2.setText("Preprocess")
        self.pushButton_2.setFixedSize(160, 80)
        self.pushButton_3 = QPushButton()
        self.pushButton_3.setText("Train")
        self.pushButton_3.setFixedSize(160, 80)
        self.pushButton_4 = QPushButton()
        self.pushButton_4.setText("Test")
        self.pushButton_4.setFixedSize(160, 80)

        # Grid Layout
        grid = QGridLayout()
        grid.addWidget(self.pushButton, 0, 0)
        grid.addWidget(self.pushButton_2, 1, 0)
        grid.addWidget(self.pushButton_3, 2, 0)
        grid.addWidget(self.pushButton_4, 3, 0)

        # Central Widget
        central_widget = QWidget()
        central_widget.setLayout(grid)
        MainWindow.setCentralWidget(central_widget)

