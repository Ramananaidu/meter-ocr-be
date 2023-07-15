import logging
from collections import namedtuple
import os
import cv2
import numpy as np
import base64
import src.meter_ocr.region_detection_yolo as region_detection_yolo
from src.meter_ocr.ocr_extraction_service import OcrExtraction


Rectangle = namedtuple('Rectangle', 'xmin ymin xmax ymax')
_logger = logging.getLogger(__name__)


class OcrRegionCombination(object):
    """ OCR Region Extraction with Yolo Model """
    def __init__(self, image_bytes_data, ocr_type):
        self.image_bytes_data = image_bytes_data
        self.ocr_type = ocr_type
        self.img_write = False

    def ocr_region_combination(self):
        """ OCR Region Combination """
        ocr_reg_list = {}
        try:
            print("*******  OCR Extraction Process is Started  *******")
            ocr_reg_list = OcrExtraction(self.image_bytes_data, self.ocr_type).ocr_extraction()
            print("*******  OCR Extraction Process is Completed  *******")
            print("*******  Region Extraction Process is Started  *******")
            region_list = self.region_extraction(self.image_bytes_data)
            print("*******  Region Extraction Process is Completed  *******")
            print(region_list)
            ocr_reg_list = self.region_ocr_iou(region_list, ocr_reg_list)
            # ocr_reg_list = self.rectangle_intersection_percentage(region_list, ocr_reg_list)
        except Exception as e:
            _logger.error("Ocr Region Combination Process is failed ! |ocr_region_combination| " + repr(e))

        return ocr_reg_list

    def region_extraction(self, image_bytes_data):
        """ Region Extraction """
        region_list = ''
        try:
            region_list, source_img = region_detection_yolo.region_detection(image_bytes_data)
            if region_list and self.img_write:
                self.__image_region_output(region_list, image_bytes_data)
        except Exception as e:
            _logger.error("Region extraction Process is failed ! |region_extraction| " + repr(e))

        return region_list

    def region_ocr_iou(self, region_list, ocr_reg_list):
        """" Region OCR IOU """
        ocr_reg_data_list = {}
        try:
            for reg_idx, i_region in enumerate(region_list):
                ra = Rectangle(i_region[1], i_region[2], i_region[3], i_region[4])
                iou_res, iou_inx = [], []
                for ocr_idx, i_ocr in enumerate(ocr_reg_list):
                    rb = Rectangle(i_ocr[0], i_ocr[1], i_ocr[2], i_ocr[3])
                    res = self.iou_area(ra, rb)
                    if res:
                        iou_res.append(res)
                        iou_inx.append(ocr_idx)
                if iou_res:
                    ocr_reg_data = ocr_reg_list[iou_inx[np.argmax(iou_res)]]
                    reg_val = i_region[0].split(' ')[0]
                    ocr_reg_data_list[reg_val] = ocr_reg_data

        except Exception as e:
            _logger.error("Region and OCR IOS Process is failed ! |region_ocr_iou| " + repr(e))

        return ocr_reg_data_list

    def iou_area(self, a, b):
        """ IOU area """
        are_res = ''
        dx = min(a.xmax, b.xmax) - max(a.xmin, b.xmin)
        dy = min(a.ymax, b.ymax) - max(a.ymin, b.ymin)
        if (dx >= 0) and (dy >= 0):
            are_res = dx * dy
            return are_res

        return are_res

    def __image_region_output(self, region_list, image_bytes_data):
        """ Image region output """
        try:
            img_bytes = base64.b64decode(image_bytes_data)
            img_array = np.frombuffer(img_bytes, dtype=np.uint8)
            source_img = cv2.imdecode(img_array, flags=cv2.IMREAD_COLOR)
            dst_img = os.getcwd() + '/data/output.jpg'
            # img = cv2.imread(source_img)
            for idx, reg_data in enumerate(region_list):
                # reg_data = i_region[0]
                cv2.rectangle(source_img, (reg_data[1], reg_data[2]), (reg_data[3], reg_data[4]), (255, 0, 0), 2)
                cv2.putText(source_img, reg_data[0], (reg_data[1], reg_data[2] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12),
                        2)
            cv2.imwrite(dst_img, source_img)
        except Exception as e:
            _logger.error("Region Detection writing Process is failed ! |__image_region_output| " + repr(e))

    def rectangle_intersection_percentage(self, region_list, ocr_reg_list):
        """ Bbox intersection % """
        ocr_reg_intersect_data = ''
        rect1 = [region_list[0][1], region_list[0][2], region_list[0][3], region_list[0][4]]
        rect2 = [ocr_reg_list[3][0], ocr_reg_list[3][1], ocr_reg_list[3][2], ocr_reg_list[3][3]]

        try:
            x_left = max(rect1[0], rect2[0])
            y_top = max(rect1[1], rect2[1])
            x_right = min(rect1[2], rect2[2])
            y_bottom = min(rect1[3], rect2[3])

            if x_right < x_left or y_bottom < y_top:
                return 0.0

            intersection_area = (x_right - x_left) * (y_bottom - y_top)
            rect1_area = (rect1[2] - rect1[0]) * (rect1[3] - rect1[1])
            rect2_area = (rect2[2] - rect2[0]) * (rect2[3] - rect2[1])
            union_area = rect1_area + rect2_area - intersection_area

            ocr_reg_intersect_data = intersection_area / union_area * 100.0

        except Exception as e:
            _logger.error("Rectangle intersection Process is failed ! |rectangle_intersection_percentage| " + repr(e))

        return ocr_reg_intersect_data
