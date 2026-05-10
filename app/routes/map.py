from flask import Blueprint, render_template, send_from_directory
from pathlib import Path

map_bp = Blueprint('map', __name__)

ROOT = Path(__file__).parent.parent.parent
MAP_DIR = Path(ROOT / 'app/static/map')
CHARTS_DIR = Path(ROOT / 'app/static/charts')

@map_bp.route('/')
def index():
    return render_template('index.html')

@map_bp.route('/map')
def map():
    return render_template('map.html')

@map_bp.route('/api/country-rates')
def country_rates():
    return send_from_directory(MAP_DIR, 'country_rates.json')

@map_bp.route('/api/corridors')
def corridors():
    return send_from_directory(MAP_DIR, 'corridors.json')

@map_bp.route('/api/charts/top-senders')
def top_senders_chart():
    return send_from_directory(CHARTS_DIR, 'top_sender_countries_chart.json')

@map_bp.route('/api/charts/top-receivers')
def top_receivers_chart():
    return send_from_directory(CHARTS_DIR, 'top_receiver_countries_chart.json')

@map_bp.route('/api/charts/hourly')
def hourly_chart():
    return send_from_directory(CHARTS_DIR, 'hourly_chart.json')

@map_bp.route('/api/charts/domestic-crossborder')
def domestic_crossborder_chart():
    return send_from_directory(CHARTS_DIR, 'domestic_vs_crossborder_chart.json')