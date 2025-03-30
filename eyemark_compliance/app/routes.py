from flask import Blueprint, render_template, jsonify
from app.utils.data_processor import DataProcessor

main = Blueprint('main', __name__)

@main.route('/')
def dashboard():
    return render_template('dash2.html')

@main.route('/api/compliance-data')
def compliance_data():
    processed_data = DataProcessor.process_compliance_data()
    if processed_data:
        return jsonify(processed_data)
    return jsonify({'error': 'Data not available'}), 500