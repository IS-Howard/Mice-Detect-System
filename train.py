from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog,QMessageBox,QInputDialog
import os
from svm import trainmodel
import shutil

#linux + docker path
#code_path_docker = '/data/.sinica_codes/gui/'
#code_path = '/home/lorsmip/.sinica_codes/gui'
#xml_path = '/home/lorsmip/sinica_data'
#video_path = '/home/lorsmip/sinica_videos'
#model_path = "/home/lorsmip/.sinica_codes/gui/yolov5/weights/mix.pt"

#windows path
code_path = '.'
xml_path = './data'
video_path = 'G:/mice_project/video'
model_path = "./yolov5/weights/mix.pt"



def makefolder(text): #xml path for each mice
    global outside_path
    outside_path = os.path.join(xml_path,text).replace('\\','/')
    os.makedirs(outside_path)

    #global docker_path  #for docker
    #docker_path = os.path.join('/data/sinica_data', text)  #for docker


class oneSet(QtWidgets.QGroupBox):
    def __init__(self, numAddWidget,label):
        QtWidgets.QGroupBox.__init__(self)
        self.numAddWidget = numAddWidget
        self.label = label
        self.initSubject()
        self.organize()

    def initSubject(self):
        self.toolButton = QtWidgets.QToolButton()
        self.toolButton.setFixedSize(21,21)
        self.toolButton.setText("...")
        self.toolButton.clicked.connect(self.read_movie_file)
        self.textEdit = QtWidgets.QLineEdit()
        #self.textEdit.setFixedSize(241, 21)
        self.label_3 = QtWidgets.QLabel()
        #self.label_3.setFixedSize(81, 16)
        self.label_3.setText("選取" + self.label + "影片{}:".format(self.numAddWidget))

    def organize(self):
        layoutH = QtWidgets.QGridLayout(self)
        layoutH.addWidget(self.label_3,0,0)
        layoutH.addWidget(self.textEdit,0,1)
        layoutH.addWidget(self.toolButton,0,3)

    def read_movie_file(self):
        filename = QFileDialog.getOpenFileName(None,"選取"+ self.label +"影片",video_path,"MP4 File (*.MP4 *.mp4)")
        self.root_movie = filename[0]
        #name = self.root_movie.split('/',3)  #for docker
        #self.root_movie = os.path.join('/data',name[3]) #for docker
        self.textEdit.setText(self.root_movie)

class detecting(QtCore.QThread):
    # trigger = QtCore.pyqtSignal(int)
    finished = QtCore.pyqtSignal()
    def __init__(self, ui, movie, xml, clss):
        super().__init__()
        self.movie = movie
        self.xml = xml
        self.ui = ui
        self.clss = clss
        with open(ui.progress_txt ,'w') as f:
            f.writelines("0\n")
    
    def run(self):
        #os.system("sudo docker exec -i sinica_running_docker python3 " + work_PWD + \
        #    "/yolov5/detect_xml.py --source {:} --facialFeature {:} --weights {:} --clss pain &".format(
        #    self.root_pain_txt, self.root_pain_xml, model))  #for docker
        #print("{:}\n{:}\n{:}\n".format(self.root_pain_movie, painxml , model))#print paths
        if self.clss == 'pain':
            os.system("python " + code_path + "/yolov5/detect_xml.py --source {:} --facialFeature {:} --weights {:} --clss pain &".format(
                self.movie, self.xml , self.ui.model))
        else:
            os.system("python " + code_path + "/yolov5/detect_xml.py --source {:} --facialFeature {:} --weights {:} --clss health &".format(
                self.movie, self.xml , self.ui.model))
        while(1):
            loop = QtCore.QEventLoop()
            QtCore.QTimer.singleShot(4000, loop.quit)
            loop.exec_()
            
            with open(self.ui.progress_txt,'r') as f:  ##############progress file
                tmp = f.readlines()
                progress = int(tmp[-1])
            print('---------------',progress,'---------------')
            self.ui.progressBar_2.setProperty("value", progress)
            if progress == 100:
                break
        self.ui.mainProgress = self.ui.mainProgress+50/self.ui.numAddWidget
        self.ui.progressBar.setProperty("value", self.ui.mainProgress)
        print("step 完成")
        self.finished.emit()
        

class Ui_train(object):
    def setupUi(self, Dialog):
        self.numAddWidget = 1
        self.saveFolder = []

        Dialog.setObjectName("Dialog")
        Dialog.resize(852, 541)
        Dialog.setWindowTitle("Trainning Windows")
        
        self.pushButton = QtWidgets.QPushButton(Dialog)
        self.pushButton.setGeometry(QtCore.QRect(340, 360, 121, 61))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.pushButton.setFont(font)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setText("Train")
        self.pushButton.clicked.connect(self.start)

        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(560, 30, 141, 41))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.label_2.setText("健康老鼠")

        self.label_4 = QtWidgets.QLabel(Dialog)
        self.label_4.setGeometry(QtCore.QRect(170, 440, 58, 15))
        self.label_4.setObjectName("label_4")
        self.label_6 = QtWidgets.QLabel(Dialog)
        self.label_6.setGeometry(QtCore.QRect(150, 480, 71, 20))
        self.label_6.setObjectName("label_6")
        self.label_4.setText("總進度")
        self.label_6.setText("段落進度")

        self.progressBar = QtWidgets.QProgressBar(Dialog)
        self.progressBar.setGeometry(QtCore.QRect(230, 440, 361, 21))
        self.progressBar.setProperty("value", 100)
        self.progressBar.setObjectName("progressBar")

        self.progressBar_2 = QtWidgets.QProgressBar(Dialog)
        self.progressBar_2.setGeometry(QtCore.QRect(230, 480, 361, 21))
        self.progressBar_2.setProperty("value", 100)
        self.progressBar_2.setObjectName("progressBar_2")

        self.pushButton_2 = QtWidgets.QPushButton(Dialog)
        self.pushButton_2.setGeometry(QtCore.QRect(800, 210, 31, 28))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.setText("+")
        self.pushButton_2.clicked.connect(self.addSet)

        self.pushButton_3 = QtWidgets.QPushButton(Dialog)
        self.pushButton_3.setGeometry(QtCore.QRect(800, 160, 31, 28))
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_3.setText("-")
        self.pushButton_3.clicked.connect(self.delSet)

        self.scrollArea = QtWidgets.QScrollArea(Dialog)
        self.scrollArea.setGeometry(QtCore.QRect(10, 70, 381, 261))
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 379, 259))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(160, 30, 151, 41))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.label.setText("疼痛老鼠")

        self.scrollArea_2 = QtWidgets.QScrollArea(Dialog)
        self.scrollArea_2.setGeometry(QtCore.QRect(400, 70, 381, 261))
        self.scrollArea_2.setWidgetResizable(True)
        self.scrollArea_2.setObjectName("scrollArea_2")
        self.scrollAreaWidgetContents_2 = QtWidgets.QWidget()
        self.scrollAreaWidgetContents_2.setGeometry(QtCore.QRect(0, 0, 379, 259))
        self.scrollAreaWidgetContents_2.setObjectName("scrollAreaWidgetContents_2")
        self.scrollArea_2.setWidget(self.scrollAreaWidgetContents_2)
        ###1 
        self.set1 = []
        self.box1 = QtWidgets.QGridLayout(self.scrollAreaWidgetContents)
        self.set1.append(oneSet(self.numAddWidget,'疼痛'))
        self.box1.addWidget(self.set1[0])
        ###2
        self.set2 = []
        self.box2 = QtWidgets.QGridLayout(self.scrollAreaWidgetContents_2)
        self.set2.append(oneSet(self.numAddWidget,'健康'))
        self.box2.addWidget(self.set2[0])
        ###
        
    def addSet(self):
        self.numAddWidget += 1
        self.set1.append(oneSet(self.numAddWidget,'疼痛'))
        self.set2.append(oneSet(self.numAddWidget,'健康'))
        self.box1.addWidget(self.set1[self.numAddWidget-1])
        self.box2.addWidget(self.set2[self.numAddWidget-1])

    def delSet(self):
        self.box1.removeWidget(self.set1[self.numAddWidget-1])
        self.set1[self.numAddWidget-1].deleteLater()
        self.set1.pop()
        self.box2.removeWidget(self.set2[self.numAddWidget-1])
        self.set2[self.numAddWidget-1].deleteLater()
        self.set2.pop()
        self.numAddWidget -= 1


    def iterate(self):
        for i in range(self.numAddWidget-1):
            self.root_pain_movie.append(self.set1[i])
            self.root_health_movie.append(self.set2[i])
            self.start(self)

    def healthstart(self):
        self.health_detect.start()

    def finish(self):
        self.msg = QMessageBox()
        self.msg.setText("Training_Finish")
        self.msg.setWindowTitle("MessageBox demo")
        retval = msg.exec_()

    def start(self):
        import os
        self.saveFolder = [] 
        for i in range(self.numAddWidget):
            text, ok = QInputDialog.getText(None, 'select save folder', '儲存資料夾名稱 {}'.format(i+1))
            if not ok:
                return
            if not os.path.isdir(xml_path + '/' + text):
                print(xml_path + text)
                self.saveFolder.append(text)
                makefolder(text)
            else:
                while(os.path.isdir(xml_path + '/' + text)):
                    msg = QMessageBox()
                    msg.setText("目的地已有該資料夾，請重新命名")
                    msg.setWindowTitle("MessageBox demo")
                    retval = msg.exec_()
                    text, ok = QInputDialog.getText(None, '', '儲存資料夾名稱 {}'.format(i+1))
                    if not ok:
                        return
                makefolder(text)
                self.saveFolder.append(text)
        self.progressBar.setProperty("value", 0)
        self.mainProgress = 0
        msgW = []
        error = 0
        for i in range(self.numAddWidget):
            self.progressBar_2.setProperty("value", 0)
            self.root_pain_movie = self.set1[i].root_movie
            self.root_health_movie = self.set2[i].root_movie

            #work_PWD = code_path_docker  #for docker
            #global docker_path  #for docker
            global outside_path

            #os.makedirs(outside_path + '/pain')#
            #os.makedirs(outside_path + '/health')#

            pxmlf = open(outside_path + "/pain.xml", "w")
            pxmlf.close()
            hxmlf = open(outside_path + "/health.xml", "w")
            hxmlf.close()
            painxml = outside_path + "/pain.xml"
            healthxml = outside_path + "/health.xml"
            #self.root_pain_xml = docker_path + '/pain.xml' #for docker
            #self.root_health_xml = docker_path + '/health.xml' #for docker
            self.progress_txt = code_path + '/progress.txt'
            self.model = model_path
            #model = work_PWD + "/yolov5/weights/mix.pt" #for docker

            #-----------------------pain------------------------------------------------------------------------
            # with open(progress_txt ,'w') as f:
            #     f.writelines("0\n")
            # #os.system("sudo docker exec -i sinica_running_docker python3 " + work_PWD + \
            # #    "maskrcnn/main_mouseDectect.py -imagesList {:} -facialFeatureLog {:} -model {:} 1 &".format(
            # #    self.root_pain_txt, self.root_pain_xml, model))  #for docker
            # #print("{:}\n{:}\n{:}\n".format(self.root_pain_movie, painxml , model))#print paths
            # os.system("python " + code_path + "/yolov5/detect_xml.py --source {:} --facialFeature {:} --weights {:} --clss pain &".format(
            # self.root_pain_movie, painxml , model))
            self.pain_detect = detecting(self, self.root_pain_movie, painxml, 'pain') 
            self.health_detect = detecting(self, self.root_health_movie, healthxml, 'health')
            self.pain_detect.start()
            self.pain_detect.finished.connect(self.healthstart)
            self.health_detect.finished.connect(self.finish)
            
            #yolo progress
            # while(1):
            #     loop = QtCore.QEventLoop()
            #     QtCore.QTimer.singleShot(4000, loop.quit)
            #     loop.exec_()
                
            #     with open(progress_txt,'r') as f:  ##############progress file
            #         tmp = f.readlines()
            #         progress = int(tmp[-1])
                
            #     self.progressBar_2.setProperty("value", progress)
            #     if progress == 100:
            #         break
            # mainProgress = mainProgress+50/self.numAddWidget
            # self.progressBar.setProperty("value", mainProgress)
            # print("pain xml 完成")

            # --------------------health------------------------------------------------------------------------------------------
        #     with open(progress_txt ,'w') as f:
        #         f.writelines("0\n")

        #     #os.system("sudo docker exec -i sinica_running_docker python3 " + work_PWD + \
        #     #    "maskrcnn/main_mouseDectect.py -imagesList {:} -facialFeatureLog {:} -model {:} 2 &".format(
        #     #    self.root_health_txt, self.root_health_xml, model))  #for docker

        #     os.system("python " + code_path + "/yolov5/detect_xml.py --source {:} --facialFeature {:} --weights {:} --clss health &".format(
        #     self.root_health_movie, healthxml , model))

        #     ###get progress
        #     while(1):
        #         loop = QtCore.QEventLoop()
        #         QtCore.QTimer.singleShot(4000, loop.quit)
        #         loop.exec_()
        #         with open(progress_txt,'r') as f:  ##############progress file
        #             tmp = f.readlines()
        #             progress = int(tmp[-1])
        #         self.progressBar_2.setProperty("value", progress)
        #         if progress == 100:
        #             break
        #     mainProgress = mainProgress+50/self.numAddWidget
        #     self.progressBar.setProperty("value", mainProgress)
        #     ###process done
        #     print("health xml 完成")

        #     #---------------svr----------------------------------------------------------------------------------------
        #     pain = outside_path + "/pain.xml"
        #     no_pain = outside_path + "/health.xml"

        #     trainNum1 = code_path + "/trainNum1.txt"
        #     trainNum2 = code_path + "/trainNum2.txt"
        #     check = True
        #     with open(trainNum1,"r") as f:
        #         if int(f.readline()) < 10:
        #             check = False
        #     with open(trainNum2,"r") as f:
        #         if int(f.readline()) < 10:
        #             check = False
            
        #     if check:
        #         trainmodel.svr(pain,no_pain,outside_path)
        #         loop = QtCore.QEventLoop()
        #         QtCore.QTimer.singleShot(4000, loop.quit)
        #         loop.exec_()
        #         mainProgress = 100*(i+1)/self.numAddWidget
        #         self.progressBar.setProperty("value", mainProgress)
        #     else:
        #         msgW.append(QMessageBox())
        #         msgW[error].setText("Training {:} less than 10 samples".format(self.saveFolder[i]))
        #         msgW[error].setWindowTitle("Warning")
        #         msgW[error].show()
        #         error = error + 1

        # msg = QMessageBox()
        # msg.setText("Training_Finish")
        # msg.setWindowTitle("MessageBox demo")
        # retval = msg.exec_()
        