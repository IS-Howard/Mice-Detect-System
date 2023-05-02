import sys
from PyQt5.QtWidgets import QApplication,QMainWindow,QDialog
from ui_window import *
from ui_load import *
from ui_preprocess import *
from ui_train import *
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
    def update_init(self):
        self.child.namelist = []
        self.child.click_sel = None
        self.show()

class preprocessWindow(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.child = preprocessor()
        self.child.initUI(self)
    def update_init(self):
        self.child.load_table()
        self.child.click_sel = None
        self.show()

class trainWindow(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.child = trainer()
        self.child.initUI(self)
    def update_init(self):
        self.child.itemlist = []
        self.child.posSet = set()
        self.child.negSet = set()
        self.child.click_sel = None
        self.child.filterbox = Filter()
        self.child.load_table()
        self.show()


if __name__=="__main__":
    # test insert
    insert_load('asdf1','Male','','34','/mnt/c/Users/x/Desktop/Mice-Detect-System/videos/m1.avi','2022','G')
    insert_load('asdf2','','10','36','/mnt/c/Users/x/Desktop/Mice-Detect-System/videos/m2.avi','2022','G')
    insert_load('asdf3','Female','15','','/mnt/c/Users/x/Desktop/Mice-Detect-System/videos/m3.avi','2022','G')
    insert_load('asdf4','Female','20','29','/mnt/c/Users/x/Desktop/Mice-Detect-System/videos/m4.avi','2022','G')
    insert_load('asdf5','Male','25','19','/mnt/c/Users/x/Desktop/Mice-Detect-System/videos/m5.avi','2022','G')
    insert_load('asdf6','','','52','/mnt/c/Users/x/Desktop/Mice-Detect-System/videos/m6.avi','2022','G')
    # insert_crop('202105',633, 1049, 404, 784)
    # insert_crop('202106',725, 1141, 333, 713)
    # insert_crop('2021',1033, 1449, 264, 644)
    insert_crop('2022',1023,1439,294,674)
    insert_load('asdf7','','','52','/mnt/c/Users/x/Desktop/Mice-Detect-System/videos/m7.avi')

    crop_init()
    load_init()
    model_init()

    app = QApplication(sys.argv)
    windows = parentWindow()
    loading = LoadWindow()
    preprocess = preprocessWindow()
    train = trainWindow()

    button1 = windows.main_ui.pushButton
    button1.clicked.connect(loading.update_init)
    button2 = windows.main_ui.pushButton_2
    button2.clicked.connect(preprocess.update_init)
    button3 = windows.main_ui.pushButton_3
    button3.clicked.connect(train.update_init)

    windows.show()
    sys.exit(app.exec_())