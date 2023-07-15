from fastapi import FastAPI, File, UploadFile, APIRouter
import uvicorn
import base64
from pydantic import BaseModel
from src.meter_ocr.region_ocr_connection import OcrRegionCombination

app = FastAPI()

router = APIRouter(
    prefix='/meter_reading',
    tags=['Meter ocr']
)

class Item(BaseModel):
    image_data: str

@router.post("/")
async def meter_image_process(meter_image: UploadFile = File(...)):
    image_bytes = await meter_image.read()
    image_data = base64.b64encode(image_bytes).decode("utf-8")
    meter_reading_data_fields = {"meter_reader_data": ''}
    ocr_type = 'paddle'
    ocr_reg_data = OcrRegionCombination(image_data, ocr_type).ocr_region_combination()
    if ocr_reg_data:
        meter_reading_data_fields = {"meter_reader_data": ocr_reg_data}
    return meter_reading_data_fields

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
