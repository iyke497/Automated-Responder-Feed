import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    EYEMARK_API_URL = "https://api.eyemark.ng/api"
    API_TOKEN = os.getenv('EYEMARK_API_TOKEN')
    ORG_ID = os.getenv('EYEMARK_ORG_ID')