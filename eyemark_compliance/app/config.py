# <--v1.03.04-->
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'sqlite:///{BASE_DIR / "instance" / "compliance.db"}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    EYEMARK_API_URL = "https://api.eyemark.ng/api"
    API_TOKEN = os.getenv('EYEMARK_API_TOKEN')
    ORG_ID = os.getenv('EYEMARK_ORG_ID')