from flask import Blueprint, render_template, jsonify, request
from app.api_client import EyemarkAPIClient
from app.data_processor import DataProcessor
import logging

main = Blueprint('main', __name__)
logger = logging.getLogger(__name__)

@main.route('/')
def dashboard():
    return render_template('dash2.html')

@main.route('/api/compliance-data')
def compliance_data():
    """Main endpoint for dashboard data"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 25))

        raw_data = EyemarkAPIClient().fetch_compliance_data()
        processed_data = DataProcessor.transform_compliance_data(raw_data)
        
        # Calculate totals for metrics
        total_compliant = sum(1 for item in processed_data if item['Status'] == 'Compliant')
        total_non_compliant = len(processed_data) - total_compliant

        # Paginate for table
        total_items = len(processed_data)
        paginated_data = processed_data[(page-1)*per_page : page*per_page]

        return jsonify({
            'success': True,
            'data': paginated_data,
            'totals': {
                'total_institutions': total_items,
                'total_compliant': total_compliant,
                'total_non_compliant': total_non_compliant,
                'compliance_rate': round((total_compliant / total_items * 100) if total_items > 0 else 0)
            },
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total_pages': (total_items + per_page - 1) // per_page
            }
        })
        
    except Exception as e:
        logger.error(f"API endpoint error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500