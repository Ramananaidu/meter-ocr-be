import fastapi
import uvicorn
from src.meter_ocr import meter_service
from src.user_registration.service import login_service
import os

app = fastapi.FastAPI()

app.include_router(login_service.router)
app.include_router(meter_service.router)

if __name__ == '__main__':
    uvicorn.run("app:app", host='127.0.0.1', port=int(os.getenv('DOCKER_PORT')), reload=True,log_level="debug")