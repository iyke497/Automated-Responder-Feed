import pandas as pd
from app.config import Config

class DataProcessor:
    @staticmethod
    def save_raw_data(data):
        """Save raw API data to Excel"""
        df = pd.DataFrame(data)
        df.to_excel(Config.RAW_DATA_PATH, index=False)
        return df

    @staticmethod
    def process_compliance_data():
        """Process raw data and calculate compliance metrics"""
        try:
            df = pd.read_excel(Config.RAW_DATA_PATH)
            
            # Example processing - implement your custom logic
            df['Status'] = df.apply(lambda row: 'Compliant' if row['compliance_score'] >= 75 else 'Non-Compliant', axis=1)
            
            # Save processed data
            df.to_excel(Config.PROCESSED_DATA_PATH, index=False)
            return df.to_dict(orient='records')
        except Exception as e:
            print(f"Processing error: {str(e)}")
            return None