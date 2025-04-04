from datetime import datetime
import re
from .extensions import db

class Institution(db.Model):
    __tablename__ = 'institutions'
    
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(255))  # Store but don't rely on this
    normalized_name = db.Column(db.String(255), unique=True, nullable=False)
    display_name = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), default='Non-Compliant')
    desk_officer = db.Column(db.String(255))
    last_synced = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Survey counts
    financial = db.Column(db.Integer, default=0)
    infrastructure = db.Column(db.Integer, default=0)
    equipment = db.Column(db.Integer, default=0)
    capacity_building = db.Column(db.Integer, default=0)
    ppp_projects = db.Column(db.Integer, default=0)

    @classmethod
    def normalize_name(cls, raw_name):
        """Standardize names for reliable matching"""
        if not raw_name:
            return ""
            
        # Remove special characters and normalize spacing
        cleaned = re.sub(r'[^a-zA-Z0-9\s]', '', raw_name)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip().lower()
        
        # Common replacements
        replacements = {
            'ctr': 'center',
            'fed': 'federal',
            'hosp': 'hospital',
            'uni': 'university',
            'tech': 'technology'
        }
        
        for abbr, full in replacements.items():
            cleaned = re.sub(rf'\b{abbr}\b', full, cleaned)
            
        return cleaned

    def update_from_api(self, api_data, survey_counts):
        """Update institution record from API response"""
        self.display_name = api_data['organization']['name']
        self.public_id = api_data['organization']['public_id']
        self.desk_officer = api_data.get('contact_officer', {}).get('full_name', '')
        
        # Update survey counts
        self.financial = survey_counts.get('financial', 0)
        self.infrastructure = survey_counts.get('infrastructure', 0)
        self.equipment = survey_counts.get('equipment', 0)
        self.capacity_building = survey_counts.get('capacity_building', 0)
        self.ppp_projects = survey_counts.get('ppp_projects', 0)
        
        self.update_status()
        self.last_synced = datetime.utcnow()

    def update_status(self):
        """Determine compliance status based on survey responses"""
        required_fields = [
            self.financial,
            self.infrastructure,
            self.equipment,
            self.capacity_building,
            self.ppp_projects
        ]
        self.status = 'Compliant' if all(x >= 1 for x in required_fields) else 'Non-Compliant'