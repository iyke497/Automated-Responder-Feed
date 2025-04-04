import click
from .extensions import db
from .data_sync import DataSyncer
from flask import current_app

@click.command(name='init-db')
def init_db_command():
    """Initialize the database"""
    db.create_all()
    click.echo("Initialized the database!")

@click.command(name='sync-data')
def sync_data_command():
    """Run data synchronization"""
    syncer = DataSyncer(current_app)
    syncer.full_sync()
    click.echo("Data synchronization complete")