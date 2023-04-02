import deeplabcut
import cv2
from argparse import ArgumentParser
import os
import shutil

config = r"./dlc_data/mars/config.yaml"

vid_path = "./datadb/basal_color.avi"
save_path = "./datadb/"
name = 'basal'
coord = [1023,1439,294,674]

# parser = ArgumentParser()
# parser.add_argument("vid_path", type=str)
# parser.add_argument("save_path", type=str)
# parser.add_argument("-c", nargs='+', type=int)
# args = parser.parse_args()
# vid_path = args.vid_path
# save_path = args.save_path
# coord = args.c

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
        shutil.copy(src,dst)
shutil.rmtree(save_folder)