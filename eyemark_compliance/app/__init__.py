# <--v1.03.04-->
from flask import Flask
from app.routes import main
import logging
from pathlib import Path

def create_app():
    # Get absolute path to templates directory
    template_dir = Path(__file__).resolve().parent.parent / 'templates'

    app = Flask(__name__, template_folder=str(template_dir))
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Register blueprints
    app.register_blueprint(main)
    
    return app


