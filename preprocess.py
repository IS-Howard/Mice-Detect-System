from PyQt5.QtWidgets import QLabel, QDialog, QGridLayout, QPushButton, QInputDialog, QListWidget, QMessageBox, QListWidgetItem, QWidget
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen
from PyQt5.QtCore import QRect, QPoint, Qt, QEventLoop, QTimer
from db import *
import cv2
import os

def getframe(vid_path):
    if not os.path.isfile(vid_path):
        return QImage('')
    cap = cv2.VideoCapture(vid_path)
    ret, frame = cap.read()
    cap.release()
    height, width, channel = frame.shape
    bytesPerLine = 3 * width
    qImg = QImage(frame.data, width, height, bytesPerLine, QImage.Format_RGB888)
    return qImg


class preprocessor(object):
    # def __init__(self):
    #     super().__init__()
    #     self.initUI()
    #     self.resize(800, 300)

    def initUI(self, Dialog):
        Dialog.setWindowTitle('Preprocess Step')
        Dialog.resize(900,500)

        # list
        self.label1 = QLabel('List of unprocessed data')
        self.list_widget = QListWidget()
        self.namelist = []
        self.list_widget.itemClicked.connect(self.item_clicked)

        # preview image
        self.label2 = QLabel('preview')
        self.image = QImage()
        self.image_label = QLabel()
        self.image_label.setPixmap(QPixmap.fromImage(self.image))
        
        # button 
        self.sall_button = QPushButton('Select All')
        self.sall_button.clicked.connect(self.select_all)
        self.clear_button = QPushButton('Clear Select')
        self.clear_button.clicked.connect(self.clear_select)
        self.edit_button = QPushButton('New Crop Setting')
        self.edit_button.clicked.connect(self.new_crop)
        self.label3 = QLabel('(for clicked item)')
        self.assign_button = QPushButton('Assign Crop Setting')
        self.assign_button.clicked.connect(self.assign_crop)
        self.label4 = QLabel('(for checked items)')
        self.genfeat_button = QPushButton('Generate features')
        self.genfeat_button.clicked.connect(self.genfeat)
        self.label5 = QLabel('(for checked items)')

        # status led
        self.led = QLabel()
        self.ledR = QPixmap("./data/ledR.png").scaled(50, 50, Qt.KeepAspectRatio)
        self.ledG = QPixmap("./data/ledG.png").scaled(50, 50, Qt.KeepAspectRatio)
        self.led.setPixmap(self.ledG)
        self.led.setFixedSize(50, 50)

        # Grid Layout
        grid = QGridLayout()
        grid.addWidget(self.label1,0,0,1,2)
        grid.addWidget(self.label2,0,2,1,2)
        grid.addWidget(self.list_widget,1,0,5,2)
        grid.addWidget(self.image_label,1,2,5,5)
        grid.addWidget(self.sall_button,6,0)
        grid.addWidget(self.clear_button,7,0)
        grid.addWidget(self.edit_button,6,2,1,3)
        grid.addWidget(self.label3,6,5,1,1)
        grid.addWidget(self.assign_button,7,2,1,3)
        grid.addWidget(self.label4,7,5,1,1)
        grid.addWidget(self.genfeat_button,8,2,1,3)
        grid.addWidget(self.label5,8,5,1,1)
        grid.addWidget(self.led,7,6,2,2)

        # Set central widget
        Dialog.setLayout(grid)

        # init list
        self.load_table()
        self.click_sel = None
        insert_crop('202105',633, 1049, 404, 784)
        insert_crop('202106',725, 1141, 333, 713)
        insert_crop('2021',1033, 1449, 264, 644)
        insert_crop('2022',1023,1439,294,674)
        insert_load('asdf7','','','52','/mnt/c/Users/x/Desktop/Mice-Detect-System/videos/m7.avi','2022','G')

    def load_table(self):
        data_all = load_load()
        self.list_widget.clear()
        self.namelist = []
        for data in data_all:
            if data[6]:
                continue
            list_item = QListWidgetItem(f"{data[0]} ({data[1]}, {data[2]}, {data[3]}) crop set:{data[5]}")
            list_item.setCheckState(0)
            self.list_widget.addItem(list_item)
            self.namelist.append(data[0])

    def select_all(self):
        for i in range(self.list_widget.count()):
            self.list_widget.item(i).setCheckState(2)

    def clear_select(self):
        for i in range(self.list_widget.count()):
            self.list_widget.item(i).setCheckState(0)

    def new_crop(self):
        if self.click_sel==None:
            return
        sel = load_load(self.namelist[self.click_sel])
        cropbox = Croper(sel)
        cropbox.exec()

    # def delete_select(self):
    #     del_names = []
    #     for i in range(self.list_widget.count()):
    #         if self.list_widget.item(i).checkState() == 2:
    #             del_names.append(self.namelist[i])
    #     if len(del_names)==0:
    #         return
    #     reply = QMessageBox.warning(None, 'Warning', 'The selected item would be deleted from data base', QMessageBox.Ok | QMessageBox.Close, QMessageBox.Close)
    #     if reply != QMessageBox.Ok:
    #         return
    #     del_load(del_names)
    #     self.load_table()
    #     self.click_sel = None

    def item_clicked(self,item):
        sel_name = self.namelist[self.list_widget.row(item)]
        self.click_sel = self.list_widget.row(item)
        self.set_image_with_crop_selection(sel_name)
        self.image_label.setPixmap(QPixmap.fromImage(self.image))
        self.image_label.update()

    def set_image_with_crop_selection(self, sel_name):
        sel = load_load(sel_name)
        vid_path = sel[4]
        sel_set = sel[5]
        self.image = getframe(vid_path)
        if sel_set:
            [sel_crop,x1,x2,y1,y2] = load_crop(sel_set)
            qp = QPainter()
            qp.begin(self.image)
            pen = QPen(Qt.red, 2, Qt.SolidLine)
            qp.setPen(pen)
            qp.drawRect(x1,y1,x2-x1,y2-y1)
            qp.end()
        self.image = self.image.scaled(600, 400, Qt.KeepAspectRatio)

    def assign_crop(self):
        inds = []
        for i in range(self.list_widget.count()):
            if self.list_widget.item(i).checkState() == 2:
                inds.append(i)
        if len(inds)==0:
            return
        selector = Crop_Selector()
        selector.exec()
        if selector.sel_crop == None:
            return
        for ind in inds:
            sel_name = self.namelist[ind]
            update_load_crop(sel_name,selector.sel_crop)
        self.load_table()
        self.click_sel = None

    def genfeat(self):
        self.led.setPixmap(self.ledR)

        save_path = './datadb/'
        inds = []
        for i in range(self.list_widget.count()):
            if self.list_widget.item(i).checkState() == 2:
                inds.append(i)
        if len(inds)==0:
            self.led.setPixmap(self.ledG)
            return
        for ind in inds:
            sel_name = self.namelist[ind]
            sel = load_load(sel_name)
            if not os.path.isfile(sel[4]) or sel[5]==None:
                continue
            [sel_crop,x1,x2,y1,y2] = load_crop(sel[5])

            os.system(f'docker exec -i dlc python3 dlc_extract.py "{sel[4]}" "{save_path}" "{sel_name}" -c {x1} {x2} {y1} {y2} &')

            # wait
            while(1):
                loop = QEventLoop()
                QTimer.singleShot(4000, loop.quit)
                loop.exec_()
                
                with open('./data/progress.txt','r') as f:
                    progress = f.read()
                print(progress)
                if progress == '1':
                    break

        self.led.setPixmap(self.ledG)
        



class Crop_Selector(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.sel_crop = None
        self.setWindowTitle('Assign crop for checked data')

    def initUI(self):
        # edit Object Button
        self.button1 = QPushButton('Select')
        self.button1.clicked.connect(self.selected)

         # list area
        self.label1 = QLabel('Select the crop setting')
        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self.item_clicked)
        self.setlist = []

        # Grid Layout
        grid = QGridLayout()
        grid.addWidget(self.label1,0,0,1,3)
        grid.addWidget(self.list_widget,1,0,3,3)
        grid.addWidget(self.button1,4,1)

        # Set central widget
        self.setLayout(grid)

        # init
        self.load_table()

    def load_table(self):
        data_all = load_crop()
        self.list_widget.clear()
        self.setlist = []
        for data in data_all:
            list_item = QListWidgetItem(f"{data[0]}")
            self.list_widget.addItem(list_item)
            self.setlist.append(data[0])

    def item_clicked(self, item):
        self.sel_crop = self.setlist[self.list_widget.row(item)]

    def selected(self):
        self.close()


class Croper(QDialog):
    def __init__(self, sel):
        super().__init__()
        self.name = sel[0]
        self.vid_path = sel[4]
        self.sel_crop = None
        self.start_point = None
        self.selection = None
        self.initUI()
        self.setWindowTitle('Create New Crop Setup')
        # self.resize(800,400)

    def initUI(self):
        # image block
        self.label1 = QLabel(f'Click and Move the crop box on image of Data {self.name}')
        self.crop_widget = Crop_Widget(self.vid_path)

        # list
        self.label2 = QLabel('Crop presets')
        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self.item_clicked)

        # button
        self.create_button = QPushButton('Create Setup')
        self.create_button.clicked.connect(self.create)
        self.remove_button = QPushButton('Remove Setup')
        self.remove_button.clicked.connect(self.remove)
        self.done_button = QPushButton('Done')
        self.done_button.clicked.connect(self.leave)

        # Grid Layout
        grid = QGridLayout()
        grid.addWidget(self.label1,0,0,1,6)
        grid.addWidget(self.crop_widget,1,0,4,6)
        grid.addWidget(self.label2,5,0,1,2)
        grid.addWidget(self.list_widget,6,0,3,2)
        grid.addWidget(self.create_button,6,3,1,2)
        grid.addWidget(self.remove_button,7,3,1,2)
        grid.addWidget(self.done_button,8,3,1,2)

        # Set central widget
        self.setLayout(grid)

        # init 
        self.load_table()

    def load_table(self):
        data_all = load_crop()
        self.list_widget.clear()
        for data in data_all:
            list_item = QListWidgetItem(f"{data[0]}")
            self.list_widget.addItem(list_item)

    def item_clicked(self,item):
        self.sel_crop = item.text()
        [sc,x1,x2,y1,y2] = load_crop(self.sel_crop)

        self.crop_widget.start_point = QPoint(x1*self.crop_widget.ratio,y1*self.crop_widget.ratio)
        self.crop_widget.gen_selection()
        self.crop_widget.update()

    def create(self):
        error_box = QMessageBox()
        error_box.setIcon(QMessageBox.Warning)
        error_box.setWindowTitle("Error")

        if self.crop_widget.selection==None:
            error_box.setText("No crop region selected!")
            error_box.exec_()
            return

        setting, ok = QInputDialog.getText(None, "Enter text", "Setting Name:")
        if not ok:
            return
        if setting == '':
            error_box.setText("Setting name is empty!")
            error_box.exec_()
            return
        
        x1,x2,y1,y2 = self.crop_widget.original_coords()

        if insert_crop(setting,x1,x2,y1,y2)==-1:
            error_box.setText("Setting name exist!")
            error_box.exec_()
            return
        list_item = QListWidgetItem(f"{setting}")
        self.list_widget.addItem(list_item)

        self.sel_crop = None
        self.crop_widget.selection = None
        self.crop_widget.update()

    def remove(self):
        if self.sel_crop==None:
            return
        del_crop(self.sel_crop)
        self.load_table()
        self.sel_crop=None

    def leave(self):
        self.close()
    
class Crop_Widget(QWidget):
    def __init__(self, vid_path):
        super().__init__()

        self.image = getframe(vid_path)
        self.selection = None
        self.start_point = None
        self.end_point = None

        self.initUI()

    def initUI(self):
        # resize and get resize ratio
        w, h = 1000, 550
        w_ratio, h_ratio = w/self.image.size().width(),  h/self.image.size().height()
        self.ratio = min(w_ratio, h_ratio) # new size / old size
        self.image = self.image.scaled(w, h, Qt.KeepAspectRatio)
        self.setFixedSize(self.image.size())
        # box size preset
        self.offx, self.offy = 416*self.ratio, 380*self.ratio

        layout = QGridLayout(self)
        layout.addWidget(self,0,0)
        self.show()

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        if self.image is not None:
            qp.drawImage(QPoint(0, 0), self.image)
        pen = QPen(Qt.red, 2, Qt.SolidLine)
        qp.setPen(pen)
        if self.selection is not None:
            qp.drawRect(self.selection)
        qp.end()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_point = event.pos()
            self.gen_selection()
            self.update()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.start_point = event.pos()
            self.gen_selection()
            self.update()

    def gen_selection(self):
        if self.start_point!=None:
            self.selection = QRect(self.start_point, QPoint(self.start_point.x()+self.offx, self.start_point.y()+self.offy))

    def original_coords(self):
        x1, y1 = self.start_point.x(), self.start_point.y()
        x2, y2 = self.selection.right(), self.selection.bottom()
        x1, y1 = x1/self.ratio, y1/self.ratio
        x2, y2 = x2/self.ratio, y2/self.ratio
        return int(x1),int(x2),int(y1),int(y2)