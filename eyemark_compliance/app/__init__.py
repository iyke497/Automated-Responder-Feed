# <--v1.03.04-->
from flask import Flask
from .config import Config
from .extensions import db
from .routes import main
import logging
from pathlib import Path

def old_create_app():
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
    
    pass

def create_app():
    # Get absolute path to templates directory
    template_dir = Path(__file__).resolve().parent.parent / 'templates'

    app = Flask(__name__, template_folder=str(template_dir))
    app.config.from_object(Config)
    
    # Initialize database
    db.init_app(app)
    

    # Register CLI commands
    from .cli import init_db_command, sync_data_command
    app.cli.add_command(init_db_command)
    app.cli.add_command(sync_data_command)

    # Import models after db initialization
    with app.app_context():
        # Register blueprints AFTER initializing extensions
        from .routes import main
        app.register_blueprint(main)

        # db.create_all()
    
    return app