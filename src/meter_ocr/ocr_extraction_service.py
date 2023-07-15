import logging
# from pytesseract import Output
# import pytesseract
# from paddleocr import PaddleOCR
import cv2
import io
import base64
import paddleocr
import numpy as np
from PIL import Image
                                                                    
# from transformers import TrOCRProcessor, VisionEncoderDecoderModel

_logger = logging.getLogger(__name__)


class OcrExtraction(object):
    """ OCR Extraction using open sources """
    def __init__(self, image_bytes_data, ocr_type):
        self.image_bytes_data = image_bytes_data
        self.ocr_type = ocr_type

    def ocr_extraction(self):
        ocr_reg_list = ''
        try:
            if self.ocr_type == 'paddle':
                ocr_reg_list = self._ocr_extraction_paddle(self.image_bytes_data)
            # elif self.ocr_type == 'tesseract':
            #     ocr_reg_list = self._ocr_extraction_tesseract(self.image_bytes_data)
            # elif self.ocr_type == 'trocr':
            #     ocr_reg_list = self._ocr_extraction_TrOCR(self.image_bytes_data)
        except Exception as e:
            _logger.error("Ocr Region Combination Process is failed ! |ocr_region_combination| " + repr(e))

        return ocr_reg_list

    def _ocr_extraction_paddle(self, image_base64):
        ocr_reg_list = ''
        try:
            image_bytes = base64.b64decode(image_base64)
            image_array = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            # ocr = paddleocr.PaddleOCR()
            ocr = paddleocr.PaddleOCR(
                det_model_dir="src/ml_model/ocr_models/paddle_models/det/",
                rec_model_dir="src/ml_model/ocr_models/paddle_models/rec/",
                cls_model_dir="src/ml_model/ocr_models/paddle_models/cls/",
                layout_model_dir="src/ml_model/ocr_models/paddle_models/layout/",
                table_model_dir="src/ml_model/ocr_models/paddle_models/table/"
            )
            result = ocr.ocr(image)
            ocr_reg_list = []
            for idx in range(len(result)):
                res = result[idx]
                for line in res:
                    xMin = round(max(line[0][0][0], line[0][3][0]))
                    yMin = round(max(line[0][0][1], line[0][1][1]))
                    xMax = round(max(line[0][1][0], line[0][2][0]))
                    yMax = round(max(line[0][2][1], line[0][3][1]))
                    ocr_reg_list.append([xMin, yMin, xMax, yMax, line[1][0], line[1][1]])
        except Exception as e:
            _logger.error("Paddle ocr extraction Process is failed ! |ocr_extraction| " + repr(e))

        return ocr_reg_list

    