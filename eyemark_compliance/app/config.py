import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    EYEMARK_API_URL = "https://api.eyemark.ng/api"
    DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data'))
    RAW_DATA_PATH = os.path.join(DATA_DIR, 'raw/institutions.xlsx')
    PROCESSED_DATA_PATH = os.path.join(DATA_DIR, 'processed/processed_data.xlsx')
    
    # Get from environment variables
    API_TOKEN = os.getenv('EYEMARK_API_TOKEN')
    ORG_ID = os.getenv('EYEMARK_ORG_ID')