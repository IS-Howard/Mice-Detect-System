from PyQt5.QtWidgets import QLabel, QDialog, QGridLayout, QPushButton, QComboBox, QListWidget, QMessageBox, QListWidgetItem, QLineEdit, QSpinBox, QInputDialog
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from db import *
from ui_load import Editor
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

class trainer(object):
    # def __init__(self):
    #     super().__init__()
    #     self.initUI()
    #     self.resize(800, 300)

    def initUI(self, Dialog):
        Dialog.setWindowTitle('Training Model Step')
        Dialog.resize(900,500)

        # all data list
        self.sall_button = QPushButton('Select All')
        self.sall_button.clicked.connect(self.select_all)
        self.clear_button = QPushButton('Clear Select')
        self.clear_button.clicked.connect(self.clear_select)
        self.filter_button = QPushButton('Filter')
        self.filter_button.clicked.connect(self.filter)
        self.resetfilter_button = QPushButton('Reset Filter')
        self.resetfilter_button.clicked.connect(self.reset_filter)
        self.listlabel = QLabel('List of data')
        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self.item_clicked)

        # edit delete in list
        self.edit_button = QPushButton('Edit Selected')
        self.edit_button.clicked.connect(self.edit)
        self.del_button = QPushButton('Delete Checked')
        self.del_button.clicked.connect(self.delete)


        # pos list
        self.listlabel2 = QLabel('Possitive (Uncomfortable)')
        self.list_widget2 = QListWidget()
        self.addpos = QPushButton('Add to Possitive ↓')
        self.addpos.clicked.connect(self.addPos)
        self.resetpos = QPushButton('Reset')
        self.resetpos.clicked.connect(self.resetPos)

        # neg list
        self.listlabel3 = QLabel('Negative (Healthy)')
        self.list_widget3 = QListWidget()
        self.addneg = QPushButton('Add to Negative ↓')
        self.addneg.clicked.connect(self.addNeg)
        self.resetneg = QPushButton('Reset')
        self.resetneg.clicked.connect(self.resetNeg)

        # train
        self.train_button = QPushButton('Start Training')
        self.train_button.clicked.connect(self.train)

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
        grid.addWidget(self.filter_button,1,3)
        grid.addWidget(self.list_widget,2,0,6,4)
        grid.addWidget(self.resetfilter_button,2,4)
        grid.addWidget(self.edit_button,3,4)
        grid.addWidget(self.del_button,4,4)

        self.list_widget.setMinimumSize(250, 200)
        grid.addWidget(self.addpos,8,0)
        grid.addWidget(self.addneg,8,2)
        grid.addWidget(self.listlabel2,9,0,1,2)
        grid.addWidget(self.listlabel3,9,2,1,2)
        grid.addWidget(self.list_widget2,10,0,2,2)
        grid.addWidget(self.list_widget3,10,2,2,2)
        grid.addWidget(self.resetpos,12,0)
        grid.addWidget(self.resetneg,12,2)
        grid.addWidget(self.train_button,12,4)
        grid.addWidget(self.led,12,5)

        # Set central widget
        Dialog.setLayout(grid)

        # init list
        # self.itemlist = []
        # self.posSet = set()
        # self.negSet = set()
        # self.click_sel = None
        # self.filterbox = Filter()
        # self.load_table()

    def load_table(self):
        data_all = load_load()
        self.list_widget.clear()
        self.itemlist = []
        for data in data_all:
            if data[6] != "G":
                continue
            list_item = QListWidgetItem(f"{data[0]}\t({data[1]},\t{data[2]},\t{data[3]})")
            list_item.setCheckState(0)
            self.list_widget.addItem(list_item)
            self.itemlist.append(item(data[0],data[1],data[2],data[3]))

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
                if os.path.isfile("./datadb/"+editbox.original_name+".feat"):
                    os.rename("./datadb/"+editbox.original_name+".feat","./datadb/"+editbox.name+".feat")

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
            featpath = csvpath.replace(".csv",".feat")
            if os.path.isfile(csvpath):
                os.remove(csvpath)
            if os.path.isfile(featpath):
                os.remove(featpath)
        del_load(del_names)
        self.load_table()
        self.click_sel = None

    def item_clicked(self,item):
        self.click_sel = self.list_widget.row(item)

    def addPos(self):
        sel_names = []
        for i in range(self.list_widget.count()):
            if self.list_widget.item(i).checkState() == 2:
                sel_names.append(self.itemlist[i].name)
        if len(sel_names)==0:
            return
        
        for name in sel_names:
            if name not in self.posSet and name not in self.negSet:
                list_item = QListWidgetItem(f"{name}")
                self.list_widget2.addItem(list_item)
                self.posSet.add(name)

    def resetPos(self):
        self.posSet.clear()
        self.list_widget2.clear()

    def addNeg(self):
        sel_names = []
        for i in range(self.list_widget.count()):
            if self.list_widget.item(i).checkState() == 2:
                sel_names.append(self.itemlist[i].name)
        if len(sel_names)==0:
            return
        
        for name in sel_names:
            if name not in self.posSet and name not in self.negSet:
                list_item = QListWidgetItem(f"{name}")
                self.list_widget3.addItem(list_item)
                self.negSet.add(name)

    def resetNeg(self):
        self.negSet.clear()
        self.list_widget3.clear()
        
    def train(self):
        error_box = QMessageBox()
        error_box.setIcon(QMessageBox.Warning)
        error_box.setWindowTitle("Error")
        if len(self.posSet)==0 or len(self.negSet)==0:
            error_box.setText("Negative or Positive data can't be empty!")
            error_box.exec_()
            return
        
        # self.posSet
        # self.negSet
        model_name, ok = QInputDialog.getText(None, 'Set Model Name', 'Model Name')
        if not ok:
            return
        elif load_model(model_name):
            error_box.setText("Model name exist!")
            error_box.exec_()
            return
        split, ok = QInputDialog.getText(None, 'Train Proportion', 'Train Proportion(0~1)')
        if not ok:
            return
        elif not is_float(split) or (float(split)<=0 or float(split)>1):
            error_box.setText("Invalid Train-Test Split!")
            error_box.exec_()
            return
        split = float(split)
        cluster, ok = QInputDialog.getText(None, 'Cluster step', 'Add cluster step? (yes or no)')
        while(cluster.lower()!='yes' and cluster.lower()!='no'):
            if not ok:
                return
            cluster, ok = QInputDialog.getText(None, 'Cluster step', 'Add cluster step? (yes or no)')

        
        self.led.setPixmap(self.ledR)
        if cluster.lower()=='yes':
            acc,fa,dr = train_model(self.posSet,self.negSet,split,model_name=model_name)
        else:
            acc,fa,dr = train_model(self.posSet,self.negSet,split,model_name=model_name,cluster=False)
        insert_model(model_name)
        self.led.setPixmap(self.ledG)

        msg = QMessageBox()
        msg.setText("testing accuracy:{:.2f}\ntesting false alarm:{:.2f}\ntesting detection rate:{:.2f}".format(acc,fa,dr))
        msg.setWindowTitle("Training_Finish")
        msg.exec_()

        

            
        

class Filter(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.setWindowTitle('Data Filter')
        self.reset()
        self.signal = 0 # 0 : no op, 1 : reset, 2: set filter

    def initUI(self):
        self.namelabel = QLabel('Name involve:')
        self.namebox = QLineEdit()
        self.genderlabel = QLabel('Gender:')
        self.genderbox = QComboBox()
        self.genderbox.addItems(["","Male", "Female"])
        self.agelabel = QLabel('Age range:')
        self.agelabel2 = QLabel('~')
        self.agebox = QSpinBox()
        self.agebox.setRange(0,999)
        self.agebox2 = QSpinBox()
        self.agebox2.setRange(0,999)
        self.weightlabel = QLabel('Weight range:')
        self.weightlabel2 = QLabel('~')
        self.weightbox = QSpinBox()
        self.weightbox.setRange(0,999)
        self.weightbox2 = QSpinBox()
        self.weightbox2.setRange(0,999)
        self.resetbutton = QPushButton('Reset')
        self.resetbutton.clicked.connect(self.reset)
        self.filter_button = QPushButton('Filter')
        self.filter_button.clicked.connect(self.setfilter)

        # Grid Layout
        grid = QGridLayout()
        grid.addWidget(self.namelabel,1,0)
        grid.addWidget(self.namebox,1,1,1,3)
        grid.addWidget(self.genderlabel,2,0)
        grid.addWidget(self.genderbox,2,1,1,2)
        grid.addWidget(self.agelabel,3,0)
        grid.addWidget(self.agebox,3,1)
        grid.addWidget(self.agelabel2,3,2)
        grid.addWidget(self.agebox2,3,3)
        grid.addWidget(self.weightlabel,4,0)
        grid.addWidget(self.weightbox,4,1)
        grid.addWidget(self.weightlabel2,4,2)
        grid.addWidget(self.weightbox2,4,3)
        grid.addWidget(self.resetbutton,5,0,1,2)
        grid.addWidget(self.filter_button,5,2,1,2)

        # Set central widget
        self.setLayout(grid)

    def reset(self):
        self.namebox.setText('')
        self.genderbox.setCurrentText('')
        self.agebox.setValue(0)
        self.agebox2.setValue(999)
        self.weightbox.setValue(0)
        self.weightbox2.setValue(999)
        self.signal = 1

    def setfilter(self):
        self.signal = 2
        self.close()
        
