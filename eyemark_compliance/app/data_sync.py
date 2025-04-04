from datetime import datetime
from collections import defaultdict
from flask import current_app
from .models import db, Institution
from .api_client import EyemarkAPIClient

class DataSyncer:
    def __init__(self, app):
        self.app = app
        self.api = EyemarkAPIClient()
        
    def full_sync(self):
        """Main synchronization workflow"""
        with self.app.app_context():
            try:
                # Fetch fresh data
                api_data = self.api.fetch_compliance_data()
                survey_counts = self._process_surveys()
                
                # Process institutions
                for inst_data in api_data:
                    self._process_institution(inst_data, survey_counts)
                
                db.session.commit()
                
            except Exception as e:
                db.session.rollback()
                raise e

    def _process_surveys(self):
        """Count survey responses by normalized names"""
        surveys = {
            'financial': self.api.fetch_survey_responses('financial-survey-id'),
            'infrastructure': self.api.fetch_survey_responses('infra-survey-id'),
            # Add other surveys
        }
        
        counts = defaultdict(lambda: defaultdict(int))
        
        for survey_type, responses in surveys.items():
            for response in responses:
                raw_name = response['organization']['name']
                norm_name = Institution.normalize_name(raw_name)
                counts[norm_name][survey_type] += 1
                
        return counts

    def _process_institution(self, api_data, survey_counts):
        """Create/update institution record"""
        raw_name = api_data['organization']['name']
        norm_name = Institution.normalize_name(raw_name)
        
        institution = Institution.query.filter_by(normalized_name=norm_name).first()
        
        if not institution:
            institution = Institution(normalized_name=norm_name)
            db.session.add(institution)
            
        # Get counts for this institution
        inst_counts = survey_counts.get(norm_name, {})
        institution.update_from_api(api_data, inst_counts)