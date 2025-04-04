# <--v1.03.04-->
from flask import Blueprint, render_template, jsonify, request
from .models import Institution  # Add this
from .extensions import db  # Add this
from .api_client import EyemarkAPIClient
from .data_processor import DataProcessor
from concurrent.futures import ThreadPoolExecutor
import logging

main = Blueprint('main', __name__)
logger = logging.getLogger(__name__)

SURVEY_MAP = {
    'financial': ('f0a3d43b-f7ee-4417-a338-7ba33ab9da14', DataProcessor.process_financial_responses),
    'infra': ('fcc992ee-ee26-4158-aa53-777a965e9d6e', DataProcessor.process_infrastructure_responses),
    'equipment': ('2bce9da9-5594-4412-8b53-bfad73806f67', DataProcessor.process_equipment_responses),
    'capacity': ('c567af0e-a4c7-4372-9853-23948d64cdd7', DataProcessor.process_capacity_responses)
}

@main.route('/')
def dashboard():
    return render_template('dash2_gridjs_cleaned.html')

@main.route('/api/compliance-data')
def compliance_data():
    institutions = Institution.query.all()
    total = len(institutions)
    compliant = sum(1 for inst in institutions if inst.computed_status == 'Compliant')

    data = []
    for inst in institutions:
        inst_dict = inst.to_dict()  # to_dict() now returns computed_status in 'status'
        data.append(inst_dict)

    return jsonify({
        'data': data,
        'totals': {
            'total_institutions': total,
            'total_compliant': compliant,
            'total_non_compliant': total - compliant,
            'compliance_rate': round((compliant / total * 100) if total > 0 else 0)
        },
    })

def build_base_institution_list(org_data: list[dict]) -> list[dict]:
    
    return [
        {
            'Institution':  DataProcessor.normalize_name(
                entry.get('organization', {}).get('name', 'N/A')
            ),
            'normalized_name': DataProcessor.normalize_name_for_matching(
                entry.get('organization', {}).get('name', '')
            ),
            'Status': 'Compliant' if entry.get('no_of_assigned_projects', 0) > 0 else 'Non-Compliant',
            'DeskOfficer': entry.get('contact_officer', {}).get('full_name', ''),
            'Financial': 0,
            'Infrastructure': 0,
            'Equipment': 0,
            'CapacityBuilding': 0
        }
        for entry in org_data
    ]

def apply_survey_counts(base_list, financial, infra, equipment, capacity):
    for institution in base_list:
        pid = institution['public_id']
        institution.update({
            'Financial': financial.get(pid, 0),
            'Infrastructure': infra.get(pid, 0),
            'Equipment': equipment.get(pid, 0),
            'CapacityBuilding': capacity.get(pid, 0)
        })
    return base_list

@main.route('/api/test')
def test():
    api_client = EyemarkAPIClient()
    eq_data = api_client.fetch_survey_responses(survey_id="2bce9da9-5594-4412-8b53-bfad73806f67")

    pr_eq_data = DataProcessor.process_equipment_responses(responses=eq_data)
    
    return render_template('dash2.html')