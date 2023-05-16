import deeplabcut
import cv2
from argparse import ArgumentParser
import os
import shutil
import pandas as pd
import numpy as np
from feature_process import *
import joblib

def cpcsv(src, dst):
    raw = pd.read_csv(src)
    raw = remove_fail(raw)
    raw.to_csv(dst,index = False)

def remove_fail(raw, complete=True):
    ind = np.arange(3,len(raw.columns),3)
    null_index = (np.array(raw.iloc[2:,3],dtype=float) < 0.5)
    for i in range(1,len(ind)):
        null_index2 = (np.array(raw.iloc[2:,ind[i]],dtype=float) < 0.5)
        null_index = np.logical_or(null_index,null_index2)
    if complete:
        raw = raw.drop(labels=2+np.where(null_index)[0], axis=0)
    else:
        raw.loc[2+np.where(null_index)[0],1:] = np.nan
    return raw

config = r"./dlc_data/mars/config.yaml"
progresstxt = r"./data/progress.txt"
with open('./data/progress.txt','w') as f:
    f.write("0")

# vid_path = "./datadb/basal_color.avi"
# save_path = "./datadb/"
# name = 'basal'
# coord = [1023,1439,294,674]

parser = ArgumentParser()
parser.add_argument("vid_path", type=str)
parser.add_argument("save_path", type=str)
parser.add_argument("name", type=str)
parser.add_argument("-c", nargs='+', type=int)
args = parser.parse_args()
vid_path = args.vid_path
save_path = args.save_path
name = args.name
coord = args.c

save_folder=save_path+'/'+ name +'/'
if not os.path.isdir(save_folder):
    os.makedirs(save_folder)
#crop video
y1,y2,x1,x2 = coord[0], coord[1], coord[2], coord[3]
fourcc = cv2.VideoWriter_fourcc(*'XVID')
cap = cv2.VideoCapture(vid_path)
out = cv2.VideoWriter(save_folder+'tmp.avi', fourcc, 30, (y2-y1,x2-x1))

while(cap.isOpened()):
    ret, frame = cap.read()
    if ret == False:
        break
    newframe = frame[x1:x2,y1:y2,:]
    out.write(newframe)
cap.release()
out.release()


deeplabcut.analyze_videos(config, save_folder+'tmp.avi', gputouse=0, save_as_csv=True, destfolder=save_folder)

gen_files = os.listdir(save_folder)
dst = save_path+'/'+name+'.csv'
for file in gen_files:
    if file.endswith('.csv'):
        src = save_folder+file
        # shutil.copy(src,dst)
        cpcsv(src,dst)
shutil.rmtree(save_folder)


### feature preprocess ###################################################################################################################
dlc_raw = read_dlc(dst)
if len(dlc_raw)>50:
    feat = count_feature(dlc_raw, feat_type='bscwtH')
    featsav = dst.replace('.csv','.feat')
    joblib.dump(feat, featsav)

#############################################################################################################################

with open('./data/progress.txt','w') as f:
    f.write("1")