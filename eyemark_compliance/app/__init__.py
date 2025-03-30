from flask import Flask
import os
from app.config import Config
from app.routes import main
from apscheduler.schedulers.background import BackgroundScheduler
import logging

def create_app():
    # Initialize Flask app
    app = Flask(__name__, template_folder='templates')
    app.config.from_object(Config)
    
    # Register blueprints
    app.register_blueprint(main)
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize scheduler
    if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        scheduler = BackgroundScheduler()
        scheduler.add_job(fetch_and_process_data, 'interval', hours=24)
        scheduler.start()
    
    return app

def fetch_and_process_data():
    """Scheduled data update job"""
    from app.utils import api_client, data_processor  # Local import to avoid circular dependency
    logging.info("Starting scheduled data update")
    
    client = api_client.EyemarkClient()
    raw_data = client.get_institutions()
    
    if raw_data:
        data_processor.DataProcessor.save_raw_data(raw_data)
        data_processor.DataProcessor.process_compliance_data()
        logging.info("Data update completed successfully")
    else:
        logging.error("Failed to update data")