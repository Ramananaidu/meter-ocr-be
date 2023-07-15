import fastapi
import uvicorn

from service import login_service
import os

app = fastapi.FastAPI()

app.include_router(login_service.router)

if __name__ == '__main__':
    uvicorn.run("app:app", host='127.0.0.1', port=int(os.getenv('DOCKER_PORT')), reload=True,log_level="debug")