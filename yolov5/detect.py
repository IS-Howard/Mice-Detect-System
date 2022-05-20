import argparse
import os
import platform
import shutil
import time
from pathlib import Path
import numpy as np

import cv2
import torch
import torch.backends.cudnn as cudnn
from numpy import random

from models.experimental import attempt_load
from utils.datasets import LoadStreams, LoadImages
from utils.general import (
    check_img_size, non_max_suppression, apply_classifier, scale_coords,
    xyxy2xywh, plot_one_box, strip_optimizer, set_logging)
from utils.torch_utils import select_device, load_classifier, time_synchronized

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
    xml.createDescriptor(name="Mask-RCNN", tag="config")
    xml.updateDescriptor(tag="configName", value=str(config.name))
    xml.updateDescriptor(tag="MODEL_DIR", value=str(MODEL_DIR))
    xml.updateDescriptor(tag="COCO_MODEL_PATH", value=str(COCO_MODEL_PATH))
    xml.updateDescriptor(tag="DETECTION_MIN_CONFIDENCE", value=str(config.DETECTION_MIN_CONFIDENCE))
    xml.updateDescriptor(tag="NUM_CLASSES", value=str(config.NUM_CLASSES))
    xml.updateDescriptor(tag="STEPS_PER_EPOCH", value=str(config.STEPS_PER_EPOCH))
    xml.saveFile()

    xml.createDescriptor(name="testVideos", tag="sourcefile")
    xml.updateDescriptor(tag="IMGLIST", value=str(args_imagesList))
    xml.updateDescriptor(tag="facialFeatureLog", value=str(args_facialFeatureLog))

    xml.saveFile()
    return 0

def recordBoxInfo(boxes, masks, class_ids, class_names, frame, scores=None):
    # num_face = sum(class_ids == 1)
    num_ear = sum(class_ids == 1)
    num_eye = sum(class_ids == 2)
    num_nose = sum(class_ids == 3)
    if (num_ear > 1) and (num_eye > 1) and (num_nose == 1):
        # Number of instances
        N = boxes.shape[0]
        if not N:
            print("\n*** No instances to display *** \n")
        else:
            assert boxes.shape[0] == masks.shape[-1] == class_ids.shape[0]

        # seperate eyes
        LeyeX = False
        ReyeX = False
        for i in range(N):
            # Bounding box
            if not np.any(boxes[i]):
                # Skip this instance. Has no bbox. Likely lost in image cropping.
                continue
            y1, x1, y2, x2 = boxes[i]
            X = x1
            # Label
            class_id = class_ids[i]
            label = class_names[class_id]
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
            y1, x1, y2, x2 = boxes[i]
            X = x1
            # Label
            class_id = class_ids[i]
            label = class_names[class_id]
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
            y1, x1, y2, x2 = boxes[i]
            X = x1
            Y = y1
            width = x2 - x1
            height = y2 - y1

            # Label
            class_id = class_ids[i]
            label = class_names[class_id]
            score = scores[i] if scores is not None else None

            if label == 'face':
                ET.SubElement(xmlFaceHandle, "bbox", frame=str(frame),
                              x=str(X), y=str(Y), width=str(width), height=str(height), score=str(score)
                              )
            elif label == 'ear':
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
    return 0





def detect(save_img=False):
    out, source, weights, view_img, save_txt, imgsz = \
        opt.output, opt.source, opt.weights, opt.view_img, opt.save_txt, opt.img_size
    webcam = source.isnumeric() or source.startswith('rtsp') or source.startswith('http') or source.endswith('.txt')

    # Initialize
    set_logging()
    device = select_device(opt.device)
    if os.path.exists(out):
        shutil.rmtree(out)  # delete output folder
    os.makedirs(out)  # make new output folder
    half = device.type != 'cpu'  # half precision only supported on CUDA

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
    if webcam:
        view_img = True
        cudnn.benchmark = True  # set True to speed up constant image size inference
        dataset = LoadStreams(source, img_size=imgsz)
    else:
        # save_img = True
        save_img = False
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
    for path, img, im0s, vid_cap in dataset:
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
        
        # # Apply Classifier
        # if classify:
        #     pred = apply_classifier(pred, modelc, img, im0s)

        ear_count = 0
        eye_count = 0
        nose_count = 0
        # print(pred[0])
        for i, det in enumerate(pred):
            if det is not None and len(det):
                for c in det[:,-1].unique():
                    if int(c) == 0:
                        ear_count = int((det[:, -1] == c).sum())
                    elif int(c) == 1:
                        eye_count = int((det[:, -1] == c).sum())
                    elif int(c) == 2:
                        nose_count = int((det[:, -1] == c).sum())

        # Process detections
    
        for i, det in enumerate(pred):  # detections per image
            if webcam:  # batch_size >= 1
                p, s, im0 = path[i], '%g: ' % i, im0s[i].copy()
            else:
                p, s, im0 = path, '', im0s
            # print(det)
            save_path = 'F:/KT_pain_frontal_face/YoloV5/CCI_TW/frame'
            save_path = save_path + str(img_name) + '.jpg'
            # save_path = str(Path(out) / Path(p).name)
            # txt_path = str(Path(out) / Path(p).stem) + ('_%g' % dataset.frame if dataset.mode == 'video' else '')
            # s += '%gx%g ' % img.shape[2:]  # print string
            gn = torch.tensor(im0.shape)[[1, 0, 1, 0]]  # normalization gain whwh
            if det is not None and len(det):
                # Rescale boxes from img_size to im0 size
                det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0.shape).round()
                for *xyxy, conf, cls in reversed(det):
                    label = '%s %.2f' % (names[int(cls)], conf)
                    plot_one_box(xyxy, im0, label=label, color=colors[int(cls)], line_thickness=3)
                
            if (ear_count == 2) and (eye_count == 2) and (nose_count == 1):
                # cv2.imwrite(save_path, im0)
                # Print results
                for c in det[:, -1].unique():
                    # print('c' ,c)
                    n = (det[:, -1] == c).sum()  # detections per class
                    s += '%g %ss, ' % (n, names[int(c)])  # add to string

            cv2.imshow(p, im0)
            if cv2.waitKey(1) == ord('q'):  # q to quit
                raise StopIteration
                # # Write results
                # for *xyxy, conf, cls in reversed(det):
                #     if save_txt:  # Write to file
                #         xywh = (xyxy2xywh(torch.tensor(xyxy).view(1, 4)) / gn).view(-1).tolist()  # normalized xywh
                #         with open(txt_path + '.txt', 'a') as f:
                #             f.write(('%g ' * 5 + '\n') % (cls, *xywh))  # label format

                #     if save_img or view_img:  # Add bbox to image
                #         label = '%s %.2f' % (names[int(cls)], conf)
                #         plot_one_box(xyxy, im0, label=label, color=colors[int(cls)], line_thickness=3)

            # Print time (inference + NMS)
            # print('%sDone. (%.3fs)' % (s, t2 - t1))

            # Stream results
            # if view_img:
            #     cv2.imshow(p, im0)
            #     if cv2.waitKey(1) == ord('q'):  # q to quit
            #         raise StopIteration

        #     # Save results (image with detections)
        #     if save_img:
        #         if dataset.mode == 'images':
        #             cv2.imwrite(save_path, im0)
        #         else:
        #             if vid_path != save_path:  # new video
        #                 vid_path = save_path
        #                 if isinstance(vid_writer, cv2.VideoWriter):
        #                     vid_writer.release()  # release previous video writer

        #                 fourcc = 'mp4v'  # output video codec
        #                 fps = vid_cap.get(cv2.CAP_PROP_FPS)
        #                 w = int(vid_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        #                 h = int(vid_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        #                 vid_writer = cv2.VideoWriter(save_path, cv2.VideoWriter_fourcc(*fourcc), fps, (w, h))
        #             vid_writer.write(im0)

        # if save_txt or save_img:
        #     print('Results saved to %s' % Path(out))
        #     if platform.system() == 'Darwin' and not opt.update:  # MacOS
        #         os.system('open ' + save_path)

        print('Done. (%.3fs)' % (time.time() - t1))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--weights', nargs='+', type=str, default='yolov5s.pt', help='model.pt path(s)')
    parser.add_argument('--source', type=str, default='inference/images', help='source')  # file/folder, 0 for webcam
    parser.add_argument('--output', type=str, default='inference/output', help='output folder')  # output folder
    parser.add_argument('--img-size', type=int, default=640, help='inference size (pixels)')
    parser.add_argument('--conf-thres', type=float, default=0.4, help='object confidence threshold')
    parser.add_argument('--iou-thres', type=float, default=0.5, help='IOU threshold for NMS')
    parser.add_argument('--device', default='', help='cuda device, i.e. 0 or 0,1,2,3 or cpu')
    parser.add_argument('--view-img', action='store_true', help='display results')
    parser.add_argument('--save-txt', action='store_true', help='save results to *.txt')
    parser.add_argument('--classes', nargs='+', type=int, help='filter by class: --class 0, or --class 0 2 3')
    parser.add_argument('--agnostic-nms', action='store_true', help='class-agnostic NMS')
    parser.add_argument('--augment', action='store_true', help='augmented inference')
    parser.add_argument('--update', action='store_true', help='update all models')
    opt = parser.parse_args()

    with torch.no_grad():
        if opt.update:  # update all models (to fix SourceChangeWarning)
            for opt.weights in ['yolov5s.pt', 'yolov5m.pt', 'yolov5l.pt', 'yolov5x.pt']:
                detect()
                strip_optimizer(opt.weights)
        else:
            detect()
