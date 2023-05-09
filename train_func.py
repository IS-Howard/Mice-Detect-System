# from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay, accuracy_score, roc_curve, RocCurveDisplay
# from sklearn.inspection import permutation_importance
# import tensorflow as tf
import numpy as np

import joblib
# import matplotlib.pyplot as plt
# cluster
# from sklearn.decomposition import PCA
# import umap
# import hdbscan
# from sklearn.cluster import SpectralClustering
from sklearn.cluster import KMeans
# from sklearn.cluster import AffinityPropagation

# from sklearn.ensemble import RandomForestClassifier
# from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.svm import SVC

def load_feat(pnames, nnames, featpath = "./datadb/"):
    #pnames:positive names, nnames:negative names
    pfeats, nfeats = [],[]
    for name in pnames:
        pfeats.append(joblib.load(featpath+'/'+name+"_feat.sav"))
    for name in nnames:
        nfeats.append(joblib.load(featpath+'/'+name+"_feat.sav"))
    return pfeats, nfeats

def train_balance(x,y):
    health = np.where(y==0)[0]
    pain = np.where(y==1)[0]
    mins = min([len(health),len(pain)])
    health = np.random.choice(health, mins, replace=False)
    pain = np.random.choice(pain, mins, replace=False)
    newidx = np.concatenate([health,pain])
    return x[newidx],y[newidx]

def motion_cluster(feat, k=50, cls_type='km'):
    if cls_type=='hdbscan':
        mcls=None
        # min_c = k
        # print("min cluster size: ", int(round(min_c * 0.01 * feat.shape[0])))
        # learned_hierarchy = hdbscan.HDBSCAN(
        #                     prediction_data=True, min_cluster_size=int(round(min_c * 0.01 * embeddings.shape[0])),
        #                     min_samples=1).fit(feat)
        # labels = learned_hierarchy.labels_
        # assign_prob = hdbscan.all_points_membership_vectors(learned_hierarchy)
        # assignments = np.argmax(assign_prob, axis=1)
    # elif cls_type=='spec':
    #     mcls = SpectralClustering(n_clusters=k, assign_labels='discretize', random_state=0).fit(feat)
    #     assignments = mcls.labels_
    elif cls_type=='km':
        mcls = KMeans(n_clusters=k).fit(feat)
        assignments = mcls.labels_
    # elif cls_type=='af':
    #     mcls =  AffinityPropagation().fit(feat)
    #     assignments = mcls.labels_
    print("motions num: ", len(np.unique(assignments)))
    return assignments, mcls

def motion_predict(feat, clf, embeder=None):
     # if is lstm => flatten to 2d feature
    if len(feat.shape)>2:
        feat = feat.reshape(len(feat), feat.shape[1]*feat.shape[2])
    if embeder:
        test_embedding = embeder.transform(feat)
    else:
        test_embedding = feat
    labels = clf.predict(test_embedding)
    return labels

def pose_cls(pfeats, nfeats, k=50, cls_type='km', clf_type='svm'):
    # get feature
    feat = np.concatenate(np.concatenate([pfeats,nfeats]))

    # if is lstm => flatten to 2d feature
    if len(feat.shape)>2:
        feat = feat.reshape(len(feat), feat.shape[1]*feat.shape[2])
    
    # cluster
    motions, mclf = motion_cluster(feat, k, cls_type)
    motion_num = len(np.unique(motions))

    # cluster predict and save result
    motionsB = [0]*motion_num
    motionsT = [0]*motion_num
    for i in range(len(nfeats)):
        motionB = motion_predict(nfeats[i], mclf)
        for j in np.unique(motions):
            motionsB[j]+= len(np.where(motionB==j)[0])
    for i in range(len(pfeats)):
        motionT = motion_predict(pfeats[i], mclf)
        for j in np.unique(motions):
            motionsT[j]+= len(np.where(motionT==j)[0])

    # motion score
    motion_num = len(motionsB)
    ratio = np.zeros((motion_num), dtype=float)
    for i in range(motion_num):
        if (motionsB[i]+motionsT[i])>0:
            ratio[i] = motionsT[i]/(motionsB[i]+motionsT[i])
    motion_score = np.zeros((motion_num), dtype=float)
    th = 0.4
    motion_score[(ratio<=th) | (ratio>=1-th)] = 1
    motion_score[(ratio>th) & (ratio<1-th)] = -1
    print("bad motions:", len(np.where(motion_score==-1)[0]))
    # plot 
    # x = np.arange(motion_num)
    # width = 0.3
    # plt.bar(x, motionsB, width, color='green', label='basal')
    # plt.bar(x + width, motionsT, width, color='red', label='treat')
    # plt.xticks(x + width / 2, x)
    # plt.legend(bbox_to_anchor=(1,1), loc='upper left')
    # plt.show()
    # plt.savefig()

    # self.mclf = mclf
    # self.motionsB = motionsB
    # self.motionsT = motionsT
    # self.motion_score = motion_score
    return motion_score, mclf

def split_dataset(feats, class_type, mclf=None, motion_score=None, split=0.5, shuffle=True, motion_del=False):
    '''
    process(motion cluster) and split each of dataset to train and test part
    class_type : 0(negative(health)), 1(positive(pain))
    split : train part ratio
    '''
    x_train,y_train,x_test,y_test = [],[],[],[]

    for feat in feats:
        # cluster step process (relabel or delete sample)
        label = np.zeros((feat.shape[0]), dtype=int)
        label[:] = class_type
        if mclf:
            motions = motion_predict(feat, mclf)
            for i in range(len(motion_score)):
                if motion_score[i] == -1:
                    if motion_del:
                        #label[np.where(motions==i)] = -1 ## bad motion label
                        label = np.delete(label,np.where(motions==0))
                        feat = np.delete(feat,np.where(motions==0),0)
                        motions = np.delete(motions,np.where(motions==0))
                    else:
                        label[np.where(motions==i)] = 0
                        feat = feat
        if shuffle:
            ind = np.arange(len(feat))
            np.random.shuffle(ind)
            feat = feat[ind]
            label = label[ind]
        if split==0:
            x_train.append(feat)
            y_train.append(label)
        else:
            sp = int(len(label)*split)
            x_train.append(feat[:sp,:])
            y_train.append(label[:sp])
            x_test.append(feat[sp:,:])
            y_test.append(label[sp:])

    x_train = np.concatenate(x_train)
    y_train = np.concatenate(y_train)
    x_test = np.concatenate(x_test)
    y_test = np.concatenate(y_test)

    return x_train,y_train,x_test,y_test

def analysis(x, y, model):
    pred = model.predict(x)

    # non-seperate
    tp = np.count_nonzero((y==1) & (pred==1))
    tn = np.count_nonzero((y==0) & (pred==0))
    fp = np.count_nonzero((y==0) & (pred==1)) # mis postive 
    fn = np.count_nonzero((y==1) & (pred==0))
    if (fp+tn)==0:
        fa = 0
    else:
        fa = fp/(fp+tn)
    if (tp+fn)==0:
        dr = 0
    else:
        dr = tp/(tp+fn)
    acc = (tp+tn)/(tp+tn+fp+fn)
    print('accuracy = ', acc)
    print("false alarm: ", fa)
    print("detection rate: ", dr)
    return acc,fa,dr


def train_model(pnames,nnames,split,model_name=None):
    pfeats, nfeats = load_feat(pnames,nnames)
    feats = pfeats
    feats.extend(nfeats)
    motion_score, mclf = pose_cls(pfeats, nfeats, k=50, cls_type='km', clf_type='svm')
    x_train_n,y_train_n,x_test_n,y_test_n = split_dataset(nfeats, 0, mclf=mclf, motion_score=motion_score, split=split, shuffle=True, motion_del=False)
    x_train_p,y_train_p,x_test_p,y_test_p = split_dataset(pfeats, 1, mclf=mclf, motion_score=motion_score, split=split, shuffle=True, motion_del=False)
    x_train = np.concatenate([x_train_n,x_train_p])
    y_train = np.concatenate([y_train_n,y_train_p])
    x_test = np.concatenate([x_test_n,x_test_p])
    y_test = np.concatenate([y_test_n,y_test_p])
    x_train,y_train = train_balance(x_train,y_train)

    model = SVC(kernel='rbf', C=1000)
    model.fit(x_train,y_train)
    if model_name:
        joblib.dump(model,'./datadb/'+model_name+'.model')
        joblib.dump(mclf, './datadb/'+model_name+'.mclf')
    if len(y_test)==0:
        return -1,-1,-1
    acc,fa,dr = analysis(x_test,y_test,model)

    return acc,fa,dr

def test_model(model_name, feats):
    model = joblib.load('./datadb/'+model_name+'.model')
    mclf = joblib.load('./datadb/'+model_name+'.mclf')

    for x in feats:
        pred = model.predict(x)



