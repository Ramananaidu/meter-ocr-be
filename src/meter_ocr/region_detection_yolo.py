# YOLOv5 🚀 by Ultralytics, GPL-3.0 license
"""

Run inference on images, videos, directories, streams, etc.

Usage - sources:
    $ python path/to/detect.py --weights yolov5s.pt --source 0              # webcam
                                                             img.jpg        # image
                                                             vid.mp4        # video
                                                             path/          # directory
                                                             path/*.jpg     # glob
                                                             'https://youtu.be/Zgi9g1ksQHc'  # YouTube
                                                             'rtsp://example.com/media.mp4'  # RTSP, RTMP, HTTP stream

Usage - formats:
    $ python path/to/detect.py --weights yolov5s.pt                 # PyTorch
                                         yolov5s.torchscript        # TorchScript
                                         yolov5s.onnx               # ONNX Runtime or OpenCV DNN with --dnn
                                         yolov5s.xml                # OpenVINO
                                         yolov5s.engine             # TensorRT
                                         yolov5s.mlmodel            # CoreML (MacOS-only)
                                         yolov5s_saved_model        # TensorFlow SavedModel
                                         yolov5s.pb                 # TensorFlow GraphDef
                                         yolov5s.tflite             # TensorFlow Lite
                                         yolov5s_edgetpu.tflite     # TensorFlow Edge TPU
"""

import argparse
import os
import sys
from pathlib import Path
import numpy as np
import logging
import base64
import torch
import torch.backends.cudnn as cudnn
from src.meter_ocr.yolo.detect import run

_logger = logging.getLogger(__name__)


def region_list_accuracy(data_list, class_info):
    """ Accuracy of region list """
    region_list = []
    for idx, i_data in enumerate(class_info):
        count_val = [i for i in data_list if i_data in i[0]]
        if count_val:
            if len(count_val) > 1:
                sort_acc = count_val[np.argmax([float(p_data[0].split(' ')[1]) for p_data in count_val if p_data[0]])]
                region_list.append(sort_acc)
            else:
                region_list.append(count_val[0])

    return region_list


def region_detection(source_base64):
    """ Region Detection """
    region_list, class_info, source_img = [], [], ''
    try:
        model_name = "src/ml_model/od_models/meter_reding_2_labels.pt"
        class_info = ['screen', 'serial_no']			  
        source_img = source_base64
        weights = Path(os.getcwd() + '/' + model_name)
        data_list = run(weights, source_img)
        region_list = region_list_accuracy(data_list, class_info)
    except Exception as e:
        _logger.error("Region Detection Process is failed ! " + repr(e))

    return region_list, str(source_img)


