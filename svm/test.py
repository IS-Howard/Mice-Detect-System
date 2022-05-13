#from sklearn.externals import joblib
import joblib
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


def test1(health, pain, test_movie, model):
    len_test = len(test_movie)
    hr_root = []
    pain_tree = ET.ElementTree(file=pain)
    health_tree = ET.ElementTree(file=health)

    LOC_name = ['Reye_LOC', 'Leye_LOC', 'Rear_LOC', 'Lear_LOC', 'nose_LOC']
    data = []

    hr_root.append(health_tree.getroot())
    hr_root.append(pain_tree.getroot())
    
    for i in range(len_test):
        hr_tree = ET.ElementTree(file=test_movie[i])
        hr_root.append(hr_tree.getroot())

    for i in range(len(hr_root)):
        test_LOC = {}
        test_child = []
        for child_of_root in hr_root[i]:
            test_child.append(child_of_root)

        for name_count in range(5):
            aaa = []
            for i in range(len(test_child[3])):
                x = (int(test_child[name_count + 3][i].attrib['x']) + int(test_child[name_count + 3][i].attrib['width']) * 0.5)
                y = (int(test_child[name_count + 3][i].attrib['y']) + int(test_child[name_count + 3][i].attrib['height']) * 0.5)
                aaa.append([x, y])
            test_LOC[LOC_name[name_count]] = aaa


        test_feature = np.array([test_LOC['Reye_LOC'], test_LOC['Leye_LOC'], test_LOC['Rear_LOC'], test_LOC['Lear_LOC'], test_LOC['nose_LOC']])

        test_feature = np.array(test_feature, dtype='int_')

        n = test_feature.shape[0]

        md_matrix = []
        for i in range(0, n):
            for j in range(i + 1, n):
                a = dist.cdist(test_feature[i], test_feature[j], metric='mahalanobis')
                b = a.diagonal()
                md_matrix.extend([b])

        test = []
        for i in range(len(md_matrix[0])):
            test.append(
                [md_matrix[0][i], md_matrix[1][i], md_matrix[2][i], md_matrix[3][i], md_matrix[4][i], md_matrix[5][i],
                md_matrix[6][i], md_matrix[7][i], md_matrix[8][i], md_matrix[9][i]])

        min_max_scale = preprocessing.MinMaxScaler()
        test = min_max_scale.fit_transform(test)
        data.append(test)

    path,name = os.path.split(model)
    fname = os.path.join(path,'result.png')

    with open(model,"rb+") as train:
        name = ['health','pain']
        value = []
        svr = joblib.load(train)

        for i in range(len(data)):
            testpredict = svr.predict(data[i])  
            if i > 1:
                test_name = test_movie[i-2].split('/')
                test_name = test_name[-1]
                test_name = test_name.split('.')
                test_name = test_name[0]

                name.append(test_name)  
            value.append(testpredict)
        plt.boxplot(value,labels=name)    
        plt.savefig(fname)
        plt.clf()
        plt.cla()
        plt.close()
        # plt.show()

    