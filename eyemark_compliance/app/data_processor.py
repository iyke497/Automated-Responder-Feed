from typing import List, Dict
from collections import defaultdict

class DataProcessor:
    @staticmethod
    def process_survey_responses(responses: List[Dict]) -> Dict[str, int]:
        """
        Count how many times each institution appears in survey responses,
        using the `verbose_body` field.
        """
        counts = defaultdict(int)

        for response in responses:
            for section in response.get("sections", []):
                for answer in section.get("answers", []):
                    for institution in answer.get("verbose_body", []):
                        public_id = institution.get("public_id")
                        if public_id:
                            counts[public_id] += 1

        return counts

    @staticmethod
    def extract_institution_stats(responses: List[Dict]) -> Dict[str, Dict[str, any]]:
        """
        Return both counts and institution names per public_id.
        """
        stats = defaultdict(lambda: {'count': 0, 'name': ''})

        for response in responses:
            for section in response.get("sections", []):
                for answer in section.get("answers", []):
                    for institution in answer.get("verbose_body", []):
                        public_id = institution.get("public_id")
                        name = institution.get("name", "Unknown Institution")
                        if public_id:
                            stats[public_id]['count'] += 1
                            stats[public_id]['name'] = name

        return stats

    @staticmethod
    def transform_compliance_data(raw_data: List[Dict], financial_data: List[Dict], infra_data: List[Dict], equipment_data: List[Dict], capacity_data: List[Dict]) -> List[Dict]:
        """
        Transform all data sources into dashboard format.
        """
        financial_counts = DataProcessor.process_survey_responses(financial_data)
        infra_counts = DataProcessor.process_survey_responses(infra_data)
        equipment_counts = DataProcessor.process_survey_responses(equipment_data)
        capacity_counts = DataProcessor.process_survey_responses(capacity_data)

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
    def _calculate_financial_score(entry: Dict) -> int:
        """
        Example scoring logic for financial survey response.
        """
        projects = entry.get('no_of_assigned_projects', 0)
        return min(projects * 2, 100)

    @staticmethod
    def _count_equipment_projects(entry: Dict) -> int:
        """
        Count equipment-related projects based on name.
        """
        project_name = entry.get('assigned_object', {}).get('name', '').lower()
        return 1 if 'equipment' in project_name else 0

    @staticmethod
    def _count_capacity_projects(entry: Dict) -> int:
        """
        Count capacity-building projects based on name.
        """
        project_name = entry.get('assigned_object', {}).get('name', '').lower()
        return 1 if 'training' in project_name or 'capacity' in project_name else 0