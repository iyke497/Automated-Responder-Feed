from typing import List, Dict

class DataProcessor:
    @staticmethod
    def transform_compliance_data(raw_data: List[Dict]) -> List[Dict]:
        """Transform Eyemark API response to dashboard format"""
        processed = []
        
        for entry in raw_data:
            try:
                processed.append({
                    'Institution': entry.get('organization', {}).get('name', 'N/A'),
                    'Status': 'Compliant' if entry.get('no_of_assigned_projects', 0) > 0 else 'Non-Compliant',
                    'DeskOfficer': "", #entry.get('user', {}).get('display_name', 'N/A'),
                    'Financial': 0, #DataProcessor._calculate_financial_score(entry),
                    'Infrastructure': 0, #entry.get('no_of_assigned_projects', 0),
                    'Equipment': 0, #DataProcessor._count_equipment_projects(entry),
                    'CapacityBuilding': 0, #DataProcessor._count_capacity_projects(entry)
                })
            except Exception as e:
                continue
                
        return processed

    @staticmethod
    def _calculate_financial_score(entry: Dict) -> int:
        """Example custom scoring logic"""
        projects = entry.get('no_of_assigned_projects', 0)
        return min(projects * 2, 100)  # Example scoring

    @staticmethod
    def _count_equipment_projects(entry: Dict) -> int:
        """Count equipment-related projects"""
        project_name = entry.get('assigned_object', {}).get('name', '').lower()
        return 1 if 'equipment' in project_name else 0

    @staticmethod
    def _count_capacity_projects(entry: Dict) -> int:
        """Count capacity building projects"""
        project_name = entry.get('assigned_object', {}).get('name', '').lower()
        return 1 if 'training' in project_name or 'capacity' in project_name else 0