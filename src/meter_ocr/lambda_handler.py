import json
import base64
from requests_toolbelt.multipart import decoder
from region_ocr_connection import OcrRegionCombination


def handler(event, context):
    """ Main Lambda Function """
    # headers = event['headers']['Content-Type']
    # post_data = base64.b64decode(event['body'])

    headers = event['params']['header']['Content-Type']
    post_data = base64.b64decode(event['body-json'])

    image_bytes = ''
    for part in decoder.MultipartDecoder(post_data, headers).parts:
        decoded_header = part.headers[b'Content-Disposition'].decode('utf-8')
        image_bytes = part.content

    image_data = base64.b64encode(image_bytes).decode("utf-8")
    ocr_type = "paddle"
    meter_reading_data_fields = ""
    try:
        ocr_reg_data = OcrRegionCombination(image_data, ocr_type).ocr_region_combination()
        if ocr_reg_data:
            meter_reading_data_fields = {"meter_reader_data": ocr_reg_data}
        print("Results : ", meter_reading_data_fields)
    except Exception as err:
        print(err)

    return {
        'statusCode': 200,
        'body': json.dumps(meter_reading_data_fields),
        'message': json.dumps('Lambda API trigger successfully...!')
    }

