# <--v1.03.04-->
from flask import Blueprint, render_template, jsonify, request
from app.api_client import EyemarkAPIClient
from app.data_processor import DataProcessor
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
    return render_template('dash2.html')

@main.route('/api/compliance-data')
def compliance_data():
    try:
        # 1. Fetch data
        api_client = EyemarkAPIClient()
        org_data = api_client.fetch_compliance_data()
        
        # 2. Process surveys (parallel)
        with ThreadPoolExecutor() as executor:
            futures = {
                'financial': executor.submit(api_client.fetch_survey_responses, 'f0a3d43b-f7ee-4417-a338-7ba33ab9da14'),
                'infra': executor.submit(api_client.fetch_survey_responses, 'fcc992ee-ee26-4158-aa53-777a965e9d6e'),
                'equipment': executor.submit(api_client.fetch_survey_responses, '2bce9da9-5594-4412-8b53-bfad73806f67'),
                'capacity': executor.submit(api_client.fetch_survey_responses, 'c567af0e-a4c7-4372-9853-23948d64cdd7')
            }
            survey_responses = {k: v.result() for k, v in futures.items()}
        
        # 3. Get counts
        financial_counts = DataProcessor.process_financial_responses(survey_responses['financial'])
        infra_counts = DataProcessor.process_infrastructure_responses(survey_responses['infra'])
        equipment_counts = DataProcessor.process_equipment_responses(survey_responses['equipment'])
        capacity_counts = DataProcessor.process_capacity_responses(survey_responses['capacity'])
        
        # 4. Build and merge data
        base_list = build_base_institution_list(org_data)

        # Apply survey counts
        for institution in base_list:
            norm_name = institution['Institution']  # Pre-normalized
            
            institution.update({
                'Institution': norm_name.title(),
                'Financial': financial_counts.get(norm_name, 0),
                'Infrastructure': infra_counts.get(norm_name, 0),
                'Equipment': equipment_counts.get(norm_name, 0),
                'CapacityBuilding': capacity_counts.get(norm_name, 0)
            })
            
            # Debug log
            logger.debug(
                f"{norm_name}: "
                f"F={institution['Financial']}, "
                f"I={institution['Infrastructure']}"
            )
        
        # Pagination logic
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 25))
        total_items = len(base_list)
        paginated_data = base_list[(page-1)*per_page : page*per_page]

        # Calculate metrics
        total_compliant = sum(1 for item in base_list if item['Status'] == 'Compliant')

        return jsonify({
            'success': True,
            'data': paginated_data,
            'totals': {
                'total_institutions': total_items,
                'total_compliant': total_compliant,
                'total_non_compliant': total_items - total_compliant,
                'compliance_rate': round((total_compliant / total_items * 100 if total_items > 0 else 0), 1)
            },
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total_items,
                'total_pages': (total_items + per_page - 1) // per_page
            }
        })
    
    except Exception as e:
        logger.error(f"Failed: {str(e)}")
        return jsonify({'error': str(e)}), 500

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
    
    return pr_eq_data