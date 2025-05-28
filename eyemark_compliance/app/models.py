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
        self.capacity_building = survey_counts.get('capacity', 0)
        self.ppp_projects = survey_counts.get('ppp_projects', 0)
        
        self.update_status()
        self.last_synced = datetime.utcnow()

    @property
    def computed_status(self):
        """Dynamically compute compliance based on survey counts."""
        return 'Compliant' if any([
            self.financial >= 1,
            self.infrastructure >= 1,
            self.equipment >= 1,
            self.capacity_building >= 1,
        ]) else 'Non-Compliant'

    def to_dict(self):
        return {
            'name': self.display_name.title(),
            'status': self.computed_status,
            'desk_officer': self.desk_officer,
            'financial': self.financial,
            'infrastructure': self.infrastructure,
            'equipment': self.equipment,
            'capacity_building': self.capacity_building,
            'ppp_projects': self.ppp_projects
        }

    def update_status(self):
        """Determine compliance status based on survey responses"""
        required_fields = [
            self.financial,
            self.infrastructure,
            self.equipment,
            self.capacity_building,
        ]
        self.status = 'Compliant' if any(x >= 1 for x in required_fields) else 'Non-Compliant'