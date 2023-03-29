import sys
from PyQt5.QtWidgets import QApplication,QMainWindow,QDialog
from window import *
from load import *
from db import *

class parentWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.main_ui = Ui_MainWindow()
        self.main_ui.setupUi(self)

class LoadWindow(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.child = Loader()
        self.child.initUI(self)


if __name__=="__main__":
    db_init()

    app = QApplication(sys.argv)
    windows = parentWindow()
    loading = LoadWindow()

    button1 = windows.main_ui.pushButton
    button1.clicked.connect(loading.show)
    # button2 = windows.main_ui.pushButton_2
    # button2.clicked.connect(testing.show)

    windows.show()
    sys.exit(app.exec_())