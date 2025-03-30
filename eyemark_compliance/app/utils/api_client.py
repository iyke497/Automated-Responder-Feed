import requests
from app.config import Config

class EyemarkClient:
    def __init__(self):
        self.base_url = Config.EYEMARK_API_URL
        self.headers = {
            'Authorization': f'Bearer {Config.API_TOKEN}',
            'Organization_id': Config.ORG_ID
        }

    def get_institutions(self):
        """Fetch compliance institutions from Eyemark API"""
        try:
            response = requests.get(
                f"{self.base_url}/users/visitor-organizations/",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API Error: {str(e)}")
            return None