from PyQt5.QtWidgets import QLabel, QDialog, QGridLayout, QPushButton, QComboBox, QListWidget, QMessageBox, QListWidgetItem, QWidget, QLineEdit, QSpinBox, QInputDialog
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from db import *
from ui_load import Editor
from ui_train import Filter
from train_func import *
import os

class item():
    def __init__(self, name, gender, age, weight):
        self.name = name
        self.gender = gender
        if age:
            self.age = int(age)
        else:
            self.age = 0
        if weight:
            self.weight = int(weight)
        else:
            self.weight = 0

def is_float(s):
    try:
        float(s) # for int, long, float and complex
    except ValueError:
        return False
    return True

class tester(object):
    # def __init__(self):
    #     super().__init__()
    #     self.initUI()
    #     self.resize(800, 300)

    def initUI(self, Dialog):
        Dialog.setWindowTitle('Testing Step')
        Dialog.resize(900,500)

        # all data list
        self.sall_button = QPushButton('Select All')
        self.sall_button.clicked.connect(self.select_all)
        self.clear_button = QPushButton('Clear Select')
        self.clear_button.clicked.connect(self.clear_select)
        self.filter_button = QPushButton('Filter')
        self.filter_button.clicked.connect(self.filter)
        self.resetfilter_button = QPushButton('Filter')
        self.resetfilter_button.clicked.connect(self.reset_filter)
        self.listlabel = QLabel('Select data')
        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self.item_clicked)

        # edit delete in list
        self.edit_button = QPushButton('Edit Selected')
        self.edit_button.clicked.connect(self.edit)
        self.del_button = QPushButton('Delete Checked')
        self.del_button.clicked.connect(self.delete)

        # model list
        self.listlabel2 = QLabel('Select model')
        self.list_widget2 = QListWidget()
        self.del_model = QPushButton('Delete Model')
        self.list_widget2.itemClicked.connect(self.item_clicked2)
        self.del_model.clicked.connect(self.delete_model)

        # test
        self.test_button = QPushButton('Start Testing')
        # self.test_button.clicked.connect(self.test)

        # status led
        self.led = QLabel()
        self.ledR = QPixmap("./data/ledR.png").scaled(50, 50, Qt.KeepAspectRatio)
        self.ledG = QPixmap("./data/ledG.png").scaled(50, 50, Qt.KeepAspectRatio)
        self.led.setPixmap(self.ledG)
        self.led.setFixedSize(50, 50)

        # Grid Layout
        grid = QGridLayout()
        grid.addWidget(self.listlabel,0,0,1,4)
        grid.addWidget(self.sall_button,1,0)
        grid.addWidget(self.clear_button,1,1)
        grid.addWidget(self.filter_button,1,2)
        grid.addWidget(self.list_widget,2,0,4,3)
        grid.addWidget(self.resetfilter_button,2,3)
        grid.addWidget(self.edit_button,3,3)
        grid.addWidget(self.del_button,4,3)

        # self.list_widget.setMinimumSize(250, 200)
        grid.addWidget(self.listlabel2,6,0,1,3)
        grid.addWidget(self.list_widget2,7,0,4,3)
        grid.addWidget(self.del_model,7,3)

        grid.addWidget(self.test_button,10,4)
        grid.addWidget(self.led,10,5)

        # Set central widget
        Dialog.setLayout(grid)

        # init list
        self.itemlist = []
        self.click_sel = None
        self.click_sel2 = None
        self.filterbox = Filter()
        self.load_table()
        self.load_model()

    def load_table(self):
        data_all = load_load()
        self.list_widget.clear()
        self.itemlist = []
        for data in data_all:
            if data[6] != "G":
                continue
            list_item = QListWidgetItem(f"{data[0]}\t({data[1]}, {data[2]}, {data[3]})")
            list_item.setCheckState(0)
            self.list_widget.addItem(list_item)
            self.itemlist.append(item(data[0],data[1],data[2],data[3]))

    def load_model(self):
        data_all = load_model()
        self.list_widget2.clear()
        for data in data_all:
            list_item = QListWidgetItem(f"{data[0]}")
            self.list_widget2.addItem(list_item)

    def reset_filter(self):
        self.filterbox.reset()
        self.load_table()

    def item_clicked(self,item):
        self.click_sel = self.list_widget.row(item)
        self.list_widget.update()

    def edit(self):
        if self.click_sel==None:
            return
        sel = load_load(self.itemlist[self.click_sel].name)
        editbox = Editor(sel)
        editbox.exec()
        if editbox.change:
            self.list_widget.takeItem(self.click_sel)
            self.list_widget.insertItem(self.click_sel, editbox.list_item)
            self.itemlist[self.click_sel].name = editbox.name
            # rename feature file
            if editbox.original_name != editbox.name:
                if os.path.isfile("./datadb/"+editbox.original_name+".csv"):
                    os.rename("./datadb/"+editbox.original_name+".csv","./datadb/"+editbox.name+".csv")
                if os.path.isfile("./datadb/"+editbox.original_name+"_feat.sav"):
                    os.rename("./datadb/"+editbox.original_name+"_feat.sav","./datadb/"+editbox.name+"_feat.sav")

    def filter(self):
        self.filterbox.signal = 0
        self.filterbox.exec()
        self.filterbox.close()
        if self.filterbox.signal == 1:
            self.reset_filter()
        elif self.filterbox.signal == 2:
            self.load_table()
            sel_name = self.filterbox.namebox.text()
            sel_gender = self.filterbox.genderbox.currentText()
            ageL,ageU = self.filterbox.agebox.value(), self.filterbox.agebox2.value()
            weightL,weightU = self.filterbox.weightbox.value(), self.filterbox.weightbox2.value()
            for i in range(len(self.itemlist)-1,-1,-1):
                if sel_name and sel_name not in self.itemlist[i].name:
                    del self.itemlist[i]
                    self.list_widget.takeItem(i)
                elif sel_gender and sel_gender != self.itemlist[i].gender:
                    del self.itemlist[i]
                    self.list_widget.takeItem(i)
                elif ageL < ageU and not ageL <= self.itemlist[i].age <= ageU:
                    del self.itemlist[i]
                    self.list_widget.takeItem(i)
                elif weightL < weightU and not weightL <= self.itemlist[i].weight <= weightU:
                    del self.itemlist[i]
                    self.list_widget.takeItem(i)

    def select_all(self):
        for i in range(self.list_widget.count()):
            self.list_widget.item(i).setCheckState(2)

    def clear_select(self):
        for i in range(self.list_widget.count()):
            self.list_widget.item(i).setCheckState(0)

    def delete(self):
        del_names = []
        for i in range(self.list_widget.count()):
            if self.list_widget.item(i).checkState() == 2:
                del_names.append(self.itemlist[i].name)
        if len(del_names)==0:
            return
        reply = QMessageBox.warning(None, 'Warning', 'The selected data would be deleted', QMessageBox.Ok | QMessageBox.Close, QMessageBox.Close)
        if reply != QMessageBox.Ok:
            return
        for name in del_names:
            csvpath = './datadb/'+name+".csv"
            featpath = csvpath.replace(".csv","_feat.sav")
            if os.path.isfile(csvpath):
                os.remove(csvpath)
            if os.path.isfile(featpath):
                os.remove(featpath)
        del_load(del_names)
        self.load_table()
        self.click_sel = None

    def delete_model(self):
        name = self.click_sel2
        if not name:
            return
        reply = QMessageBox.warning(None, 'Warning', 'The selected model would be deleted', QMessageBox.Ok | QMessageBox.Close, QMessageBox.Close)
        if reply != QMessageBox.Ok:
            return
        
        path1 = './datadb/'+name+".model"
        path2 = path1.replace(".model",".mclf")
        if os.path.isfile(path1):
            os.remove(path1)
        if os.path.isfile(path2):
            os.remove(path2)
        del_model(name)
        self.load_model()
        self.click_sel2 = None

    def item_clicked(self,item):
        self.click_sel = self.list_widget.row(item)

    def item_clicked2(self,item):
        self.click_sel2 = item.text()