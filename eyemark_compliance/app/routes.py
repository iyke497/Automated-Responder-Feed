# routes.py (updated)
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

# @main.route('/api/compliance-data')
# def compliance_data():
#     try:
#         api_client = EyemarkAPIClient()
        
#         # Parallel fetch all data sources
#         with ThreadPoolExecutor(max_workers=5) as executor:
#             # Submit all fetch tasks
#             future_org = executor.submit(api_client.fetch_compliance_data)
#             future_surveys = {
#                 key: executor.submit(api_client.fetch_survey_responses, survey_id)
#                 for key, (survey_id, _) in SURVEY_MAP.items()
#             }
            
#             # Get results
#             org_data = future_org.result(timeout=30)
#             survey_responses = {
#                 key: future.result(timeout=30)
#                 for key, future in future_surveys.items()
#             }

#         # Process survey data
#         processed_surveys = {}
#         for key, responses in survey_responses.items():
#             processor = SURVEY_MAP[key][1]
#             processed_surveys[key] = processor(responses)

#         # Build and enrich data
#         dashboard_data = build_base_institution_list(org_data)
#         dashboard_data = apply_survey_counts(
#             dashboard_data,
#             processed_surveys['financial'],
#             processed_surveys['infra'],
#             processed_surveys['equipment'],
#             processed_surveys['capacity']
#         )
        

#         # Pagination logic
#         page = int(request.args.get('page', 1))
#         per_page = int(request.args.get('per_page', 25))
#         total_items = len(dashboard_data)
#         paginated_data = dashboard_data[(page-1)*per_page : page*per_page]

#         # Calculate metrics
#         total_compliant = sum(1 for item in dashboard_data if item['Status'] == 'Compliant')
        
#         return jsonify({
#             'success': True,
#             'data': paginated_data,
#             'totals': {
#                 'total_institutions': total_items,
#                 'total_compliant': total_compliant,
#                 'total_non_compliant': total_items - total_compliant,
#                 'compliance_rate': round((total_compliant / total_items * 100 if total_items > 0 else 0), 1)
#             },
#             'pagination': {
#                 'page': page,
#                 'per_page': per_page,
#                 'total': total_items,
#                 'total_pages': (total_items + per_page - 1) // per_page
#             }
#         })
        
#     except Exception as e:
#         logger.error(f"API endpoint error: {str(e)}")
#         return jsonify({'success': False, 'error': str(e)}), 500

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

        print(type(financial_counts))
        # ... others
        
        # 4. Build and merge data
        base_list = build_base_institution_list(org_data)
        dashboard_data = apply_survey_counts(
            base_list,
            financial_counts,
            infra_counts,
            equipment_counts,
            capacity_counts
        )
        
        # Pagination logic
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 25))
        total_items = len(dashboard_data)
        paginated_data = dashboard_data[(page-1)*per_page : page*per_page]

        # Calculate metrics
        total_compliant = sum(1 for item in dashboard_data if item['Status'] == 'Compliant')

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
            'Institution': entry.get('organization', {}).get('name', 'N/A'),
            'public_id': entry.get('organization', {}).get('public_id', '').replace('-', '').lower(),
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