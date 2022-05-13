import sys
from PyQt5.QtWidgets import QApplication,QMainWindow,QDialog
from test import *
from train import *
from window import *

class parentWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.main_ui = Ui_MainWindow()
        self.main_ui.setupUi(self)

class trainWindow(QDialog):
    def __init__(self):
        QDialog.__init__(self)

        self.child = Ui_train()
        self.child.setupUi(self)

class testWindow(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.child = Ui_Test()
        self.child.setupUi(self)




# if __name__=="__main__":
#
#     app = QApplication(sys.argv)
#     windows = parentWindow()
#     windows.show()
#    sys.exit(app.exec_())

if __name__=="__main__":

    app = QApplication(sys.argv)
    windows = parentWindow()
    training = trainWindow()
    testing = testWindow()

    trainbutton = windows.main_ui.pushButton
    trainbutton.clicked.connect(training.show)

    testbutton = windows.main_ui.pushButton_2
    testbutton.clicked.connect(testing.show)

    windows.show()
    sys.exit(app.exec_())