import xml.etree.cElementTree as ET
import numpy as np
import scipy.spatial.distance as dist
from sklearn.svm import SVR
from sklearn.model_selection import KFold
from sklearn.model_selection import GridSearchCV
import joblib
from sklearn import preprocessing
from sklearn.model_selection import train_test_split


def svr(pain_tree_root, nopain_tree_root, save_root):
    # pain.xml
    pain_tree = ET.ElementTree(file=pain_tree_root)
    # nopain.xml
    nopain_tree = ET.ElementTree(file=nopain_tree_root)
    pain_root = pain_tree.getroot()
    nopain_root = nopain_tree.getroot()

    save_root = save_root + r'/train.train'
    #print("save_root")
    nopain_child = []
    child = []
    for child_of_root in pain_root:
        child.append(child_of_root)
    for child_of_root in nopain_root:
        nopain_child.append(child_of_root)
    # build pain feature
    pain = {}
    health = {}
    LOC_name = ['Reye_LOC', 'Leye_LOC', 'Rear_LOC', 'Lear_LOC', 'nose_LOC']
    for name_count in range(5):
        aaa = []
        print(len(child[3]))
        for i in range(len(child[3])):
            # frame = (child[name_count + 3][i].attrib['frame']
            x = (int(child[name_count + 2][i].attrib['x']) + int(child[name_count + 2][i].attrib['width']) * 0.5)
            y = (int(child[name_count + 2][i].attrib['y']) + int(child[name_count + 2][i].attrib['height']) * 0.5)
            # height = (child[name_count + 3][i].attrib['height'])
            # width = (child[name_count + 3][i].attrib['width'])
            aaa.append([x, y])
        pain[LOC_name[name_count]] = aaa

    for name_count in range(5):
        aaa = []
        for i in range(len(nopain_child[3])):
            x = (int(nopain_child[name_count + 2][i].attrib['x']) + int(
                nopain_child[name_count + 2][i].attrib['width']) * 0.5)
            y = (int(nopain_child[name_count + 2][i].attrib['y']) + int(
                nopain_child[name_count + 2][i].attrib['height']) * 0.5)
            aaa.append([x, y])
        health[LOC_name[name_count]] = aaa

    pain_feature = np.array([pain['Reye_LOC'], pain['Leye_LOC'], pain['Rear_LOC'], pain['Lear_LOC'], pain['nose_LOC']])
    health_feature = np.array(
        [health['Reye_LOC'], health['Leye_LOC'], health['Rear_LOC'], health['Lear_LOC'], health['nose_LOC']])


    pain_feature = np.array(pain_feature,dtype='int_')
    health_feature = np.array(health_feature,dtype='int_')

    # calculate mahalanobis distance and write down the input file of SVM
    n = pain_feature.shape[0]
    pain = []
    no_pain = []

    b = []
    # create positive sample to fed SVM
    for i in range(0, n):
        for j in range(i + 1, n):
            a = dist.cdist(health_feature[i], health_feature[j], metric='mahalanobis')
            b = a.diagonal()
            no_pain.extend([b])

    # create negative sample to fed SVM
    for i in range(0, n):
        for j in range(i + 1, n):
            a = dist.cdist(pain_feature[i], pain_feature[j], metric='mahalanobis')
            b = a.diagonal()
            pain.extend([b])

    c = []
    hurt = []
    health = []

    for i in range(len(pain[0])):
        dd = pain[0][i]
        hurt.append([dd, pain[1][i]/dd, pain[2][i]/dd, pain[3][i]/dd, pain[4][i]/dd, pain[5][i]/dd, pain[6][i]/dd, pain[7][i]/dd,
                      pain[8][i]/dd, pain[9][i]/dd])
        #hurt.append([pain[0][i], pain[1][i], pain[2][i], pain[3][i], pain[4][i], pain[5][i], pain[6][i], pain[7][i],
        #             pain[8][i], pain[9][i]])
    for i in range(len(no_pain[0])):
        dd = no_pain[0][i]
        health.append([dd, no_pain[1][i]/dd, no_pain[2][i]/dd, no_pain[3][i]/dd, no_pain[4][i]/dd, no_pain[5][i]/dd,
                       no_pain[6][i]/dd, no_pain[7][i]/dd, no_pain[8][i]/dd, no_pain[9][i]/dd])
        #health.append([no_pain[0][i], no_pain[1][i], no_pain[2][i], no_pain[3][i], no_pain[4][i], no_pain[5][i],
        #               no_pain[6][i], no_pain[7][i], no_pain[8][i], no_pain[9][i]])

    min_max_scale = preprocessing.MinMaxScaler()
    pain = min_max_scale.fit_transform(hurt)
    health = min_max_scale.fit_transform(health)
    svr = GridSearchCV(SVR(kernel='linear', gamma=0.1), cv=5,
                       param_grid={"C": [1e0, 1e1, 1e2, 1e3],
                                   "gamma": np.logspace(-2, 2, 5)})
    y = ['1'] * len(hurt) + ['-1'] * len(health)
    y = np.array(y, dtype='int_')

    kf = KFold(n_splits=10, shuffle=True, random_state=None)
    best_pain = 100
    best_health = 100
    X = np.vstack((pain,health))

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
    # model = svr.fit(X_train, y_train)

    # with open(save_root, "wb+") as train:
    #    joblib.dump(svr, train)
    #    train.close()


    for pain_test_index, pain_train_index in kf.split(pain):
         pain_x_train, pain_x_test = pain[pain_train_index], pain[pain_test_index]
         pain_y_train, pain_y_test = y[pain_train_index], y[pain_test_index]
         for health_test_index, health_train_index in kf.split(health):
             x_train, x_test = np.vstack((pain_x_train, health[health_train_index])), np.vstack(
                 (pain_x_test, health[health_test_index]))
             y_train, y_test = np.hstack((pain_y_train, y[len(hurt) + health_train_index])), np.hstack(
                 (pain_y_test, y[len(hurt) + health_test_index]))
             model = svr.fit(x_train, y_train)
             svr_predict = svr.predict(x_test)
             sum_pain = 0
             sum_health = 0
             for i in svr_predict[0:len(pain_y_test)]:
                 sum_pain += (i - 5) ** 2
             for i in svr_predict[len(pain_y_test):-1]:
                 sum_health += (i + 5) ** 2
             loss_pain = sum_pain / len(pain_y_test)
             loss_health = sum_health / (len(y_test) - len(pain_y_test))
             print(sum_pain / len(pain_y_test))
             print(sum_health / (len(y_test) - len(pain_y_test)))
             if (loss_health <= best_health) & (loss_pain <= best_pain):
                 print(svr.predict(x_test))
                 with open(save_root, "wb+") as train:
                     joblib.dump(svr, train)
                     train.close()
                 best_health = loss_health
                 best_pain = loss_pain
                 print("done")
                 print("*" * 50)
