from typing import List, Dict
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

class DataProcessor:
    @staticmethod
    def process_financial_responses(responses: List[Dict]) -> Dict[str, int]:
        return DataProcessor._count_responses_by_public_id(responses)

    @staticmethod
    def process_infrastructure_responses(responses: List[Dict]) -> Dict[str, int]:
        return DataProcessor._count_responses_by_public_id(responses)

    @staticmethod
    def process_equipment_responses(responses: List[Dict]) -> Dict[str, int]:
        return DataProcessor._count_responses_by_public_id(responses)

    @staticmethod
    def process_capacity_responses(responses: List[Dict]) -> Dict[str, int]:
        return DataProcessor._count_responses_by_public_id(responses)

    @staticmethod
    def _count_responses_by_public_id(responses: List[Dict]) -> Dict[str, int]:
        """
        Count how many times each institution appears in survey responses,
        using the `verbose_body` field.
        """
        counts = defaultdict(int)

        for response in responses:
            for section in response.get("sections", []):
                for answer in section.get("answers", []):
                    for institution in answer.get("verbose_body", []):
                        raw_id = institution.get("public_id", "")
                        public_id = raw_id.replace("-", "").strip().lower()  # Strip hyphens
                        if public_id:
                            logger.debug(f"[Survey] ID: {public_id} | Count: {counts[public_id]}")
                            counts[public_id] += 1

        return counts

    @staticmethod
    def transform_compliance_data(
        raw_data: List[Dict],
        financial_counts: Dict[str, int],
        infra_counts: Dict[str, int],
        equipment_counts: Dict[str, int],
        capacity_counts: Dict[str, int]
    ) -> List[Dict]:
        """
        Match institutions to their response counts and build the dashboard table structure.
        """
        processed = []

        for entry in raw_data:
            try:
                org = entry.get('organization', {})
                public_id = org.get('public_id')

                processed.append({
                    'Institution': org.get('name', 'N/A'),
                    'public_id': public_id,
                    'Status': 'Compliant' if entry.get('no_of_assigned_projects', 0) > 0 else 'Non-Compliant',
                    'Financial': financial_counts.get(public_id, 0),
                    'Infrastructure': infra_counts.get(public_id, 0),
                    'Equipment': equipment_counts.get(public_id, 0),
                    'CapacityBuilding': capacity_counts.get(public_id, 0),
                    'DeskOfficer': ""
                })
            except Exception:
                continue

        return processed

    @staticmethod
    def transform_compliance_data_from_lists(
        org_data: List[Dict],
        financial_counts: Dict[str, int],
        infra_counts: Dict[str, int],
        equipment_counts: Dict[str, int],
        capacity_counts: Dict[str, int]
    ) -> List[Dict]:
        """
        Build dashboard rows by checking each org's public_id against pre-processed response counts.
        """
        dashboard_rows = []

        for entry in org_data:
            try:
                org = entry.get('organization', {})
                raw_id = org.get('public_id', '')
                public_id = raw_id.replace('-', '').strip().lower()
                name = org.get('name', 'N/A')
                status = 'Compliant' if entry.get('no_of_assigned_projects', 0) > 0 else 'Non-Compliant'

                # Inside transform_compliance_data_from_lists loop
                logger.debug(
                    "ID: %s | Financial: %s | Infra: %s",
                    public_id,
                    financial_counts.get(public_id, 0),
                    infra_counts.get(public_id, 0)
)

                dashboard_rows.append({
                    'Institution': name,
                    'Status': status,
                    'DeskOfficer': None,  # Add if available
                    'Financial': financial_counts.get(public_id, 0),
                    'Infrastructure': infra_counts.get(public_id, 0),
                    'Equipment': equipment_counts.get(public_id, 0),
                    'CapacityBuilding': capacity_counts.get(public_id, 0)
                })
            except Exception:
                continue

        return dashboard_rows
