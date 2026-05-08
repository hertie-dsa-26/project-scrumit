from flask import Blueprint, render_template, send_from_directory, send_file
from pathlib import Path
import os

map_bp = Blueprint('map', __name__)
ROOT = Path(__file__).parent.parent.parent

@map_bp.route('/')
def index():
    return render_template('index.html')

@map_bp.route('/map')
def map():
    return render_template('map.html')

@map_bp.route('/api/country-rates')
def country_rates():
    return send_from_directory(Path(ROOT / 'app/static/map'), 'country_rates.json')

@map_bp.route('/api/corridors')
def corridors():
    return send_from_directory(Path(ROOT / 'app/static/map'), 'corridors.json')

# adding routes for the sidebar graphs
@map_bp.route('/api/charts/top-senders')
def top_senders_chart():
    return send_file('data/processed/charts/top_sender_countries_chart.json')

@map_bp.route('/api/charts/top-receivers')
def top_receivers_chart():
    return send_file('data/processed/charts/top_receiver_countries_chart.json')