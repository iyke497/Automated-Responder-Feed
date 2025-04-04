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
            'financial': self.api.fetch_survey_responses('f0a3d43b-f7ee-4417-a338-7ba33ab9da14'),
            'infrastructure': self.api.fetch_survey_responses('fcc992ee-ee26-4158-aa53-777a965e9d6e'),
            'equipment': self.api.fetch_survey_responses('2bce9da9-5594-4412-8b53-bfad73806f67'),
            'capacity': self.api.fetch_survey_responses('c567af0e-a4c7-4372-9853-23948d64cdd7'),
            'ppp': self.api.fetch_survey_responses('4a86cfb1-3e20-41d4-8c83-d304bd102102')
        }
        
        counts = defaultdict(lambda: defaultdict(int))
        
        for survey_type, responses in surveys.items():
            for response in responses:
                # Iterate through all sections
                for section in response.get('sections', []):
                    # Iterate through all answers in each section
                    for answer in section.get('answers', []):
                        # Check if verbose_body exists and is a list
                        verbose_body = answer.get('verbose_body', [])
                        for entry in verbose_body:
                            # Extract name and public_id safely
                            raw_name = entry.get('name', '')
                            public_id = entry.get('public_id', '')
                            
                            # Normalize name using Institution method
                            norm_name = Institution.normalize_name(raw_name)
                            
                            # Update counts
                            if norm_name:
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