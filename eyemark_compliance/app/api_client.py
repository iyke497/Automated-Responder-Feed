import requests
import logging
from app.config import Config

class EyemarkAPIClient:
    def __init__(self):
        self.base_url = Config.EYEMARK_API_URL
        self.headers = {
            'Authorization': f'Bearer {Config.API_TOKEN}',
            'Organization_id': Config.ORG_ID
        }
        self.logger = logging.getLogger(__name__)

    def fetch_compliance_data(self):
        """Fetch all paginated compliance data"""
        try:
            url = f"{self.base_url}/users/visitor-organizations/"
            all_results = []

            while url:
                response = requests.get(url, headers=self.headers)
                response.raise_for_status()
                data = response.json()
                
                all_results.extend(data.get('results', []))
                url = data.get('next')  # Handle pagination

            self.logger.info(f"Fetched {len(all_results)} institutions")
            return all_results

        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request failed: {str(e)}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}")
            return []
        
    def fetch_survey_responses(self, survey_id):
        """Fetch all paginated responses for a specific survey"""
        try:
            url = f"{self.base_url}/surveys/{survey_id}/responses/"
            all_results = []

            while url:
                response = requests.get(url, headers=self.headers)
                response.raise_for_status()
                data = response.json().get('data', {})
                all_results.extend(data.get('results', []))
                url = data.get('next')

            return all_results

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Survey {survey_id} request failed: {str(e)}")
            return []