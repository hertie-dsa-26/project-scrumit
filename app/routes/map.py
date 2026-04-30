from flask import Blueprint, render_template
from analysis.visuals.utils import compute_country_rates
import pandas as pd
from flask import jsonify

map_bp = Blueprint('map', __name__)

df = pd.read_csv('data/processed/aml_clean.csv')

@map_bp.route('/')
def index():
    """World map view"""
    return render_template('index.html')

@map_bp.route('/map')
def map():
    """World map view"""
    return render_template('map.html')

@map_bp.route('/api/country-rates')
def country_rates():
    return jsonify(compute_country_rates(df))