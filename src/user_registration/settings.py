from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import logging
from dotenv import load_dotenv
import os

load_dotenv()  # take environment variables from .env.

db_user = os.getenv('DB_USER')
db_pass = os.getenv('DB_PASS')
db_port = os.getenv('DB_PORT')
db_server = os.getenv('DB_SERVER')
db_name = os.getenv('DB_NAME')

# from service import logger
# from service import logger

engine = create_engine(f'postgresql://{db_user}:{db_pass}@{db_server}:{db_port}/{db_name}')
SessionLocal = sessionmaker(autoflush=False, bind=engine)
Base = declarative_base()
print('connected')



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


SECRET_KEY = 'lemoncode21'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_MINUTES = 45


# Create a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Define the log file path
log_file_path = "src/user_registration/logs/user.log"

# Ensure the directory for the log file exists
log_dir = os.path.dirname(log_file_path)
os.makedirs(log_dir, exist_ok=True)

# Create a file handler
handler = logging.FileHandler(filename=log_file_path)
handler.setLevel(logging.INFO)

# Create a formatter
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)

logger.addHandler(handler)
