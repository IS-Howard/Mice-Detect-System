import os
from svm import trainmodel

p = './1.mp4'
w = './weights/mix.pt'
n = 'test'
xm = './data/pain.xml'
code_path = 'D:/code/py_project/gui-yolo-mod'
root_pain_movie = 'D:/mice_project/video/1.mp4'
painxml = 'D:/code/py_project/gui-yolo-mod/data/1/pain.xml'
model = './yolov5/weights/mix.pt'

#os.system('python detect.py --source {:} --weights {:}'.format(p,w))
#os.system('python detect_xml.py --source {:} --weights {:} --facialFeature {:} --clss pain'.format(p,w,xm))
#os.system("python " + code_path + "/yolov5/detect_xml.py --source {:} --facialFeature {:} --weights {:} --clss pain".format(
#    root_pain_movie, painxml , model))


outside = 'D:/code/py_project/gui-yolo-mod/data/1'
pain = outside + '/pain.xml'
no_pain = outside + '/health.xml'

trainmodel.svr(pain,no_pain,outside)

