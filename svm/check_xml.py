from sklearn.externals import joblib
import xml.etree.cElementTree as ET
import numpy as np
import scipy.spatial.distance as dist
from sklearn import preprocessing
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import pyqtgraph as pg
import os 


def check_xml(xmlfile):
    hr_root = []
    tree = ET.ElementTree(file=xmlfile)

    hr_root = tree.getroot()

    test_child = []
    for child_of_root in hr_root:
        test_child.append(child_of_root)

    # print(test_child)
    a = len(test_child[3])
    

    if a < 10:
        return False
    else:
        return True


    
    
check = []
test = []   
xml1 = '/home/lorsmip/sinica_data/fbfb/test1.xml'
xml2 = '/home/lorsmip/sinica_data/fbfb/test2.xml'
xml3 = '/home/lorsmip/sinica_data/fbfb/test3.xml'
xml4 = '/home/lorsmip/sinica_data/fbfb/test4.xml'
test.append(xml1)
test.append(xml2)
test.append(xml3)
test.append(xml4)
for i in test:
    check.append(check_xml(i))
for i in range(len(check)):
    if check[i]:
        print('a')
    else:
        print('b')
# aa = check_xml(xml)
# print(aa)