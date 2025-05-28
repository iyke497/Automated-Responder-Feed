# <--v1.03.04-->
from flask import Blueprint, render_template, jsonify
from .models import Institution
from .extensions import db
import logging

main = Blueprint('main', __name__)
logger = logging.getLogger(__name__)

# TODO: Delete
# SURVEY_MAP = {
#     'financial': ('f0a3d43b-f7ee-4417-a338-7ba33ab9da14', DataProcessor.process_financial_responses),
#     'infra': ('fcc992ee-ee26-4158-aa53-777a965e9d6e', DataProcessor.process_infrastructure_responses),
#     'equipment': ('2bce9da9-5594-4412-8b53-bfad73806f67', DataProcessor.process_equipment_responses),
#     'capacity': ('c567af0e-a4c7-4372-9853-23948d64cdd7', DataProcessor.process_capacity_responses)
# }

@main.route('/')
def dashboard():
    return render_template('dashboard.html')

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
