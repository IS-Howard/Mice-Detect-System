import numpy as np
import torch
import torch.nn as nn
from models.common import Conv, DWConv
from utils.google_utils import attempt_download
from torchvision.models import vgg19


import argparse
import os
import platform
import shutil
import time
from pathlib import Path
import numpy as np
import xml.etree.cElementTree as ET
import cv2
import torch
import torch.backends.cudnn as cudnn
from numpy import random
import yaml
from models.experimental import attempt_load
from utils.datasets import LoadStreams, LoadImages
from utils.general import (
    check_img_size, non_max_suppression, apply_classifier, scale_coords,
    xyxy2xywh, plot_one_box, strip_optimizer, set_logging)
from utils.torch_utils import select_device, load_classifier, time_synchronized


#code_path = '/data/.sinica_codes/gui' #linux docker
code_path = './' #windows

class xmlManager(object):
    def __init__(self, filePath):
        self.root = ET.Element("root")
        self.filePath = filePath
        self.handle=[]

    def createDescriptor(self, name, tag):
        self.handle = []
        self.handle = ET.SubElement(self.root, str(tag), name=str(name))
        return self.handle

    def updateDescriptor(self, tag, value):
        ET.SubElement(self.handle, str(tag)).text = str(value)

    def saveFile(self):
        tree = ET.ElementTree(self.root)
        tree.write(self.filePath)

def xmlConfigWritting():
    xml.createDescriptor(name="YoloV5", tag="config")
    xml.updateDescriptor(tag="configName", value='MouseFace')
    xml.updateDescriptor(tag="Yolo_MODEL_PATH", value=str(opt.weights))
    xml.updateDescriptor(tag="DETECTION_MIN_CONFIDENCE", value=str(opt.conf_thres))
    xml.updateDescriptor(tag="NUM_CLASSES", value=str('5'))
    xml.saveFile()

    xml.createDescriptor(name="testVideos", tag="sourcefile")
    xml.updateDescriptor(tag="TestVideo", value=str(opt.source))
    xml.updateDescriptor(tag="FacialFeatureLog", value=str(opt.facialFeature))

    xml.saveFile()
    return 0

def recordBoxInfo(boxes, class_names, frame, scores=None):
    # num_face = sum(class_ids == 1)
    N = len(boxes)
    # seperate eyes
    LeyeX = False
    ReyeX = False
    for i in range(N):
        # Bounding box
        if not np.any(boxes[i]):
            # Skip this instance. Has no bbox. Likely lost in image cropping.
            continue
        x1, y1, x2, y2 = boxes[i]
        X = x1
        # Label
        label = class_names[i]
        if label == 'eye':
            if not (LeyeX or ReyeX):
                LeyeX = int(X)
                ReyeX = int(X)
            else:
                if int(X) < LeyeX:
                    LeyeX = int(X)
                elif int(X) > ReyeX:
                    ReyeX = int(X)
    # seperate ears
    LearX = False
    RearX = False
    for i in range(N):
        # Bounding box
        if not np.any(boxes[i]):
            # Skip this instance. Has no bbox. Likely lost in image cropping.
            continue
        x1, y1, x2, y2 = boxes[i]
        X = x1
        # Label
        label = class_names[i]
        if label == 'ear':
            if not (LearX or RearX):
                LearX = int(X)
                RearX = int(X)
            else:
                if int(X) < LearX:
                    LearX = int(X)
                elif int(X) > RearX:
                    RearX = int(X)

    for i in range(N):
        # Bounding box
        if not np.any(boxes[i]):
            # Skip this instance. Has no bbox. Likely lost in image cropping.
            continue
        x1, y1, x2, y2 = boxes[i]
        X = x1
        Y = y1
        width = x2 - x1
        height = y2 - y1

        # Label
        label = class_names[i]
        score = scores[i] if scores is not None else None

        if label == 'ear':
            if int(X) == LearX:
                ET.SubElement(xmlLearHandle, "bbox", frame=str(frame),
                                x=str(X), y=str(Y), width=str(width), height=str(height), score=str(score)
                                )
            elif int(X) == RearX:
                ET.SubElement(xmlRearHandle, "bbox", frame=str(frame),
                                x=str(X), y=str(Y), width=str(width), height=str(height), score=str(score)
                                )
        elif label == 'eye':
            if int(X) == LeyeX:
                ET.SubElement(xmlLeyeHandle, "bbox", frame=str(frame),
                                x=str(X), y=str(Y), width=str(width), height=str(height), score=str(score)
                                )
            elif int(X) == ReyeX:
                ET.SubElement(xmlReyeHandle, "bbox", frame=str(frame),
                                x=str(X), y=str(Y), width=str(width), height=str(height), score=str(score)
                                )
        elif label == 'nose':
            ET.SubElement(xmlNoseHandle, "bbox", frame=str(frame),
                            x=str(X), y=str(Y), width=str(width), height=str(height), score=str(score)
                            )
    return 1

class Ensemble(nn.ModuleList):
    # Ensemble of models
    def __init__(self):
        super(Ensemble, self).__init__()

    def forward(self, x, augment=False):
        y = []
        for module in self:
            y.append(module(x, augment)[0])
        # y = torch.stack(y).max(0)[0]  # max ensemble
        # y = torch.cat(y, 1)  # nms ensemble
        y = torch.stack(y).mean(0)  # mean ensemble
        return y, None  # inference, train output



def detect(save_img=False):
    out, source, weights, view_img, save_txt, imgsz, facialFeatureLog, clss = \
        opt.output, opt.source, opt.weights, opt.view_img, opt.save_txt, opt.img_size, opt.facialFeature, opt.clss
    webcam = source.isnumeric() or source.startswith('rtsp') or source.startswith('http') or source.endswith('.txt')

    # Initialize
    set_logging()
    device = select_device(opt.device)
    if os.path.exists(out):
        shutil.rmtree(out)  # delete output folder
    os.makedirs(out)  # make new output folder
    half = device.type != 'cpu'  # half precision only supported on CUDA
    half = False
    get = 0
    progress = code_path + '/progress.txt'

    # Load model
    model = attempt_load(weights, map_location=device)  # load FP32 model
    imgsz = check_img_size(imgsz, s=model.stride.max())  # check img_size
    if half:
        model.half()  # to FP16

    # Second-stage classifier
    classify = False
    if classify:
        modelc = load_classifier(name='resnet101', n=2)  # initialize
        modelc.load_state_dict(torch.load('weights/resnet101.pt', map_location=device)['model'])  # load weights
        modelc.to(device).eval()

    # Set Dataloader
    vid_path, vid_writer = None, None

    dataset = LoadImages(source, img_size=imgsz)

    # Get names and colors
    names = model.module.names if hasattr(model, 'module') else model.names
    colors = [[random.randint(0, 255) for _ in range(3)] for _ in range(len(names))]

    # Run inference
    t0 = time.time()
    img = torch.zeros((1, 3, imgsz, imgsz), device=device)  # init img
    _ = model(img.half() if half else img) if device.type != 'cpu' else None  # run once

    img_name = 0
    t1 = time_synchronized()



    cv2.waitKey(0)
    for path, img, im0s, vid_cap in dataset:
        maxBarLen = dataset.nframes

        img = torch.from_numpy(img).to(device)
        img = img.half() if half else img.float()  # uint8 to fp16/32
        img /= 255.0  # 0 - 255 to 0.0 - 1.0
        img_name += 1
        if img.ndimension() == 3:
            img = img.unsqueeze(0)

        # Inference
        
        pred = model(img, augment=opt.augment)[0]
        # Apply NMS
        pred = non_max_suppression(pred, opt.conf_thres, opt.iou_thres, classes=opt.classes, agnostic=opt.agnostic_nms)
        t2 = time_synchronized()
        
        # models = Ensemble()
        # for w in weights if isinstance(weights,list) else [weights]:
        #     attempt_load(w)
        #     models.append(torch.load(w, map_location=device)['model'].float().fuse().eval())
        #     print(models)
        # # Apply Classifier
        # if classify:
        #     pred = apply_classifier(pred, modelc, img, im0s)
        ear_count = 0
        eye_count = 0
        nose_count = 0
        # print(pred[0])
        p, s, im0 = path, '', im0s
        for i, det in enumerate(pred):
            if det is not None and len(det):
                for c in det[:,-1].unique():
                    if int(c) == 0:
                        ear_count = int((det[:, -1] == c).sum())
                    elif int(c) == 1:
                        eye_count = int((det[:, -1] == c).sum())
                    elif int(c) == 2:
                        nose_count = int((det[:, -1] == c).sum())
        #save_path = 'F:/KT_pain_frontal_face/YoloV5/CCI_TW/frame'
        # Process detections
    
        for i, det in enumerate(pred):  # detections per image
            # print(det)
            #save_img_name = save_path + str(img_name) + '.jpg'
            # save_path = str(Path(out) / Path(p).name)
            # txt_path = str(Path(out) / Path(p).stem) + ('_%g' % dataset.frame if dataset.mode == 'video' else '')
            # s += '%gx%g ' % img.shape[2:]  # print string
            gn = torch.tensor(im0.shape)[[1, 0, 1, 0]]  # normalization gain whwh
            if det is not None and len(det):
                # Rescale boxes from img_size to im0 size
                det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0.shape).round()
                # r = {'rois','class_name'}
                # print(r)
                r = {}
                roi = []
                classname = []
                score = []
                for *xyxy, conf, cls in reversed(det):
                    # label = '%s %.2f' % (names[int(cls)])
                    labels = names[int(cls)]
                    boxes = []
                    for i in range(len(xyxy)):
                        boxes.append(int(xyxy[i]))
                    roi.append(boxes)
                    score.append(float(conf))
                    classname.append(labels)    
                    plot_one_box(xyxy, im0, label=labels, color=colors[int(cls)], line_thickness=3)
                # 前面兩個是頂點座標，後面兩個是對象頂點座標
                r['rois'] = roi
                r['class_name'] = classname

                # print(len(r['rois']))
            if (ear_count == 2) and (eye_count == 2) and (nose_count == 1):
                # cv2.imwrite(save_img_name, im0)

                get = get + recordBoxInfo(r['rois'], r['class_name'], img_name, score)
                xml.saveFile()
                # for c in det[:, -1].unique():
                    
                #     n = (det[:, -1] == c).sum()  # detections per class
                #     s += '%g %ss, ' % (n, names[int(c)])  # add to string
            cframe = dataset.frame
            if ((cframe % int(maxBarLen / 100) == 0) | (cframe == maxBarLen)):
                with open(progress ,'a') as f:
                    f.writelines(str(int(cframe / maxBarLen * 100))+'\n')

            # cv2.imshow(p, im0)
            # cv2.waitKey(0)
            if cv2.waitKey(1) == ord('q'):  # q to quit
                raise StopIteration
    
        # print('Done. (%.3fs)' % (time.time() - t1))

    if clss == 'pain':
        trainNum = code_path + '/trainNum1.txt'
    else:
        trainNum = code_path + '/trainNum2.txt'
    with open(trainNum,"w") as f:
        f.writelines(str(get))
    with open(progress ,'a') as f:
        f.writelines("100"+'\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--weights', nargs='+', type=str, default='weights/mix.pt', help='model.pt path(s)')
    parser.add_argument('--source', type=str, default='inference/images', help='source')  # file/folder, 0 for webcam
    parser.add_argument('--output', type=str, default='inference/output', help='output folder')  # output folder
    parser.add_argument('--img-size', type=int, default=640, help='inference size (pixels)')
    parser.add_argument('--conf-thres', type=float, default=0.7, help='object confidence threshold')
    parser.add_argument('--iou-thres', type=float, default=0.5, help='IOU threshold for NMS')
    parser.add_argument('--device', default='0', help='cuda device, i.e. 0 or 0,1,2,3 or cpu')
    parser.add_argument('--view-img', action='store_true', help='display results')
    parser.add_argument('--save-txt', action='store_true', help='save results to *.txt')
    parser.add_argument('--classes', nargs='+', type=int, help='filter by class: --class 0, or --class 0 2 3')
    parser.add_argument('--agnostic-nms', action='store_true', help='class-agnostic NMS')
    parser.add_argument('--augment', action='store_true', help='augmented inference')
    parser.add_argument('--update', action='store_true', help='update all models')
    parser.add_argument('--facialFeature',type=str, help='.xml file of facial feature')
    parser.add_argument('--clss', type=str, help='health or pain')
    opt = parser.parse_args()

    with torch.no_grad():
        if opt.update:  # update all models (to fix SourceChangeWarning)
            for opt.weights in ['yolov5s.pt', 'yolov5m.pt', 'yolov5l.pt', 'yolov5x.pt']:
                detect()
                strip_optimizer(opt.weights)
        else:
            xml = xmlManager(filePath=opt.facialFeature)
            xmlConfigWritting()
            xmlReyeHandle = xml.createDescriptor(name="Reye", tag="attribute")
            xmlLeyeHandle = xml.createDescriptor(name="Leye", tag="attribute")
            xmlRearHandle = xml.createDescriptor(name="Rear", tag="attribute")
            xmlLearHandle = xml.createDescriptor(name="Lear", tag="attribute")
            xmlNoseHandle = xml.createDescriptor(name="nose", tag="attribute")
            xml.saveFile()
            detect()
