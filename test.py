from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog,QInputDialog,QMessageBox
from svm import test as t
import os
import shutil
import xml.etree.cElementTree as ET


#linux + docker path
#code_path_docker = '/data/.sinica_codes/gui/'
#code_path = '/home/lorsmip/.sinica_codes/gui'
#xml_path = '/home/lorsmip/sinica_data'
#video_path = '/home/lorsmip/sinica_videos'
#model_path = "/home/lorsmip/.sinica_codes/gui/yolov5/weights/mix.pt"

#windows path
code_path = '.'
xml_path = './data'
video_path = './data'
model_path = "./yolov5/weights/mix.pt"

def check_xml(xmlfile):
    tree = ET.ElementTree(file=xmlfile)

    hr_root = tree.getroot()

    test_child = []
    for child_of_root in hr_root:
        test_child.append(child_of_root)

    a = len(test_child[3])

    if a == 0:
        return False
    else:
        return True

class oneVideo(QtWidgets.QGroupBox):
    def __init__(self, numAddWidget2):
        QtWidgets.QGroupBox.__init__(self)
        self.numAddWidget2 = numAddWidget2
        self.root_movie = ''
        self.docker_movie = ''
        self.initSubject()
        self.organize()

    def initSubject(self):
        self.label_2 = QtWidgets.QLabel()
        self.label_2.setText("測試影片{}:".format(self.numAddWidget2))
        self.lineEdit_2 = QtWidgets.QLineEdit() 
        self.toolButton_4 = QtWidgets.QToolButton()
        self.toolButton_4.setFixedSize(21, 21)
        self.toolButton_4.setText("...")
        self.toolButton_4.clicked.connect(self.read_movie)

    def organize(self):
        layoutV = QtWidgets.QGridLayout(self)
        layoutV.addWidget(self.label_2,0,0)
        layoutV.addWidget(self.lineEdit_2,0,1)
        layoutV.addWidget(self.toolButton_4,0,2)

    def read_movie(self):
        filename = QFileDialog.getOpenFileName(None,"選取老鼠影片{}".format(self.numAddWidget2),video_path,"MP4 File (*.MP4 *.mp4)")
        self.root_movie = filename[0]
        self.lineEdit_2.setText(self.root_movie)


class oneModel(QtWidgets.QGroupBox):
    def __init__(self, numAddWidget):
        QtWidgets.QGroupBox.__init__(self)
        self.numAddWidget = numAddWidget
        self.numAddWidget2 = 1
        self.model_path = ''
        self.address = ''
        self.initSubject()
        self.organize()

    def initSubject(self):
        self.modelBox = QtWidgets.QGroupBox()
        self.modelBox.setFixedSize(281,60) #281 45
        self.addBtn = QtWidgets.QGroupBox()
        self.addBtn.setFixedSize(60,60) # 60 40
        self.lineEdit = QtWidgets.QLineEdit()
        self.toolButton = QtWidgets.QToolButton()
        self.toolButton.setFixedSize(21, 21)
        self.toolButton.setText("...")
        self.toolButton.clicked.connect(self.read_model)
        self.label = QtWidgets.QLabel()
        self.label.setText("訓練模型{}:".format(self.numAddWidget))
        self.pushButton_4 = QtWidgets.QPushButton()
        self.pushButton_4.setFixedSize(20, 20)
        self.pushButton_4.setText("-")
        self.pushButton_4.clicked.connect(self.delVideo)
        self.pushButton_5 = QtWidgets.QPushButton()
        self.pushButton_5.setFixedSize(20, 20)
        self.pushButton_5.setText("+")
        self.pushButton_5.clicked.connect(self.addVideo)

        self.scrollArea_2 = QtWidgets.QScrollArea()
        self.scrollArea_2.setFixedSize(281, 291)
        self.scrollArea_2.setWidgetResizable(True)
        self.scrollAreaWidgetContents_2 = QtWidgets.QWidget()
        self.scrollArea_2.setWidget(self.scrollAreaWidgetContents_2)

        self.set2 = []
        self.box2 = QtWidgets.QGridLayout(self.scrollAreaWidgetContents_2)
        self.set2.append(oneVideo(self.numAddWidget2))
        self.box2.addWidget(self.set2[0])

    def organize(self):
        layout1 = QtWidgets.QGridLayout(self.modelBox)
        layout1.addWidget(self.label,1,0)
        layout1.addWidget(self.lineEdit,1,1)
        layout1.addWidget(self.toolButton,1,2)
        layout2 = QtWidgets.QGridLayout(self.addBtn)
        layout2.addWidget(self.pushButton_4,0,0)
        layout2.addWidget(self.pushButton_5,0,1)
        layoutH = QtWidgets.QGridLayout(self)
        layoutH.addWidget(self.modelBox,0,0)
        layoutH.addWidget(self.addBtn,1,0)
        layoutH.addWidget(self.scrollArea_2,2,0)

    def addVideo(self):
        self.numAddWidget2 += 1
        self.set2.append(oneVideo(self.numAddWidget2))
        self.box2.addWidget(self.set2[self.numAddWidget2-1])

    def delVideo(self):
        self.box2.removeWidget(self.set2[self.numAddWidget2-1])
        self.set2[self.numAddWidget2-1].deleteLater()
        self.set2.pop()
        self.numAddWidget2 -= 1

    def read_model(self):
        filename = QFileDialog.getOpenFileName(None, "選取訓練模型", xml_path,"train File (*.train)")
        self.root_model = filename[0]
        self.lineEdit.setText(self.root_model)
        self.model_path = self.root_model.split('/train.train')[0]

class detecting(QtCore.QThread):
    finished = QtCore.pyqtSignal()
    def __init__(self, ui):
        super().__init__()
        self.ui = ui
    
    def run(self):
        for i in range(self.ui.numAddWidget):
            progress_txt = code_path + '/progress.txt'
            global_path = self.ui.set1[i].model_path
            test_address = global_path + '/tests'
            if not os.path.isdir(test_address):
                os.makedirs(test_address)
            check = []
            
            model = model_path

            files = [_ for _ in os.listdir(test_address) if _.endswith('.xml')]
            test = [_ for _ in files if 'test' in _]
            if len(test) == 0:
                maximum_test = 0
            else:
                test.sort(key=lambda x:int(x[4:-4]))
                maximum_test = int(test[-1][4:-4])
            
            for j in range(self.ui.set1[i].numAddWidget2):
                self.ui.progressBar_2.setProperty("value", 0)
                testnum = j + 1 + maximum_test
                movie = self.ui.set1[i].set2[j].root_movie
                testxml = test_address + '/test{}.xml'.format(testnum)

                if not os.path.isfile(testxml):
                    cf = open(testxml,"w")
                    cf.close()
               
                ###############################yolo############################################################
                with open(progress_txt ,'w') as f:
                    f.writelines("0\n")
                os.system("python " + code_path + "/yolov5/detect_xml.py --source {:} --facialFeature {:} --weights {:} --clss pain &"\
                        .format(movie, testxml , model))
                
                while(1):
                    loop = QtCore.QEventLoop()
                    QtCore.QTimer.singleShot(4000, loop.quit)
                    loop.exec_()
                    with open(progress_txt,'r') as f:  ##############progress file
                        tmp = f.readlines()
                        progress = int(tmp[-1])
                    self.ui.progressBar_2.setProperty("value", progress)
                    if progress == 100:
                        break
                print('face detect 完成')
                self.ui.mainProgress = self.ui.mainProgress+100/(self.ui.numAddWidget*self.ui.set1[i].numAddWidget2)
                self.ui.progressBar.setProperty("value", self.ui.mainProgress)
                ###process done
                
                if check_xml(testxml) == True:
                    check.append(True)
                else:
                    check.append(False)
                # with open(trainNum1,"r") as f:
                #     if int(f.readline()) == 0:
                #         check[j] = False
                # shutil.rmtree(global_path + '/test{}'.format(j + 1 + maximum_test))
                
            ########### predict plot ################################################################
            pain = global_path + '/pain.xml'
            no_pain = global_path + '/health.xml'

            test_movie = []
            previous = []
            for j in range(maximum_test):
                previous.append(check_xml(test_address + '/test{}.xml'.format(j + 1)))

            for j in range(maximum_test):     
                if previous[j] == True:
                    test_movie.append(test_address + '/test{}.xml'.format(j + 1))

            for j in range(self.ui.set1[i].numAddWidget2):
                if check[j]:
                    test_movie.append(test_address + '/test{}.xml'.format(j + 1 + maximum_test))
                else:
                    path = global_path.split('/')
                    folder_name = path[-1]
                    self.ui.msgW.append(QMessageBox())
                    self.ui.msgW[self.ui.error].setText("Testing Model:{:} No.{:} no samples".format(folder_name, j + 1 + maximum_test))
                    self.ui.msgW[self.ui.error].setWindowTitle("Warning")
                    #msgW[self.ui.error].show()
                    self.ui.error = self.ui.error + 1

            model1 = self.ui.set1[i].root_model #global_path + '/train.train'
            save_name = "result.png"

            t.test1(no_pain,pain,test_movie,model1, save_name) #save in model path
        print("step 完成")
        self.finished.emit()


class Ui_Test(object):
    def setupUi(self, Dialog):
        self.numAddWidget = 1
        self.saveFolder = []

        Dialog.setObjectName("Dialog")
        Dialog.resize(993, 590)
        Dialog.setWindowTitle("Testiing Window")

        self.pushButton = QtWidgets.QPushButton(Dialog)
        self.pushButton.setGeometry(QtCore.QRect(780, 430, 151, 61))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.pushButton.setFont(font)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setText("Test")
        self.pushButton.clicked.connect(self.starttest)

        self.scrollArea = QtWidgets.QScrollArea(Dialog)
        self.scrollArea.setGeometry(QtCore.QRect(40, 20, 691, 461))
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 689, 459))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        #
        self.set1 = []
        self.box1 = QtWidgets.QHBoxLayout(self.scrollAreaWidgetContents)
        self.set1.append(oneModel(self.numAddWidget))
        self.box1.addWidget(self.set1[0])
        #
        self.pushButton_2 = QtWidgets.QPushButton(Dialog)
        self.pushButton_2.setGeometry(QtCore.QRect(750, 110, 31, 28))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.setText("+")
        self.pushButton_2.clicked.connect(self.addSet)
        self.pushButton_3 = QtWidgets.QPushButton(Dialog)
        self.pushButton_3.setGeometry(QtCore.QRect(750, 60, 31, 28))
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_3.setText("-")
        self.pushButton_3.clicked.connect(self.delSet)
        self.progressBar = QtWidgets.QProgressBar(Dialog)
        self.progressBar.setGeometry(QtCore.QRect(610, 510, 361, 21))
        self.progressBar.setProperty("value", 100)
        self.progressBar.setObjectName("progressBar")
        self.label_4 = QtWidgets.QLabel(Dialog)
        self.label_4.setGeometry(QtCore.QRect(550, 510, 58, 15))
        self.label_4.setObjectName("label_4")
        self.label_4.setText("總進度")
        self.label_6 = QtWidgets.QLabel(Dialog)
        self.label_6.setGeometry(QtCore.QRect(530, 550, 71, 20))
        self.label_6.setObjectName("label_6")
        self.label_6.setText("段落進度")
        self.progressBar_2 = QtWidgets.QProgressBar(Dialog)
        self.progressBar_2.setGeometry(QtCore.QRect(610, 550, 361, 21))
        self.progressBar_2.setProperty("value", 100)
        self.progressBar_2.setObjectName("progressBar_2")

    def addSet(self):
        self.numAddWidget += 1
        self.set1.append(oneModel(self.numAddWidget))
        self.box1.addWidget(self.set1[self.numAddWidget-1])

    def delSet(self):
        self.box1.removeWidget(self.set1[self.numAddWidget-1])
        self.set1[self.numAddWidget-1].deleteLater()
        self.set1.pop()
        self.numAddWidget -= 1

    def finish(self):
        for i in range(self.error):
            self.msgW[i].exec()
        self.msg = QMessageBox()
        self.msg.setText("Testing_Finish")
        self.msg.setWindowTitle("MessageBox demo")
        retval = self.msg.exec_()


    def starttest(self):

        self.progressBar.setProperty("value", 0)
        self.mainProgress = 0
        self.test_movie = []
        self.error = 0
        self.msgW = []

        self.detect_process = detecting(self)
        self.detect_process.start()
        self.detect_process.finished.connect(self.finish)