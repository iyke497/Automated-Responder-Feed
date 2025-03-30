from flask import Blueprint, render_template, jsonify
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
        # Fetch and process data
        raw_data = EyemarkAPIClient().fetch_compliance_data()
        processed_data = DataProcessor.transform_compliance_data(raw_data)
        
        return jsonify({
            'success': True,
            'data': processed_data,
            'count': len(processed_data)
        })
        
    except Exception as e:
        logger.error(f"API endpoint error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500