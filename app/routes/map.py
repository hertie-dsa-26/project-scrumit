from flask import Blueprint, render_template

map_bp = Blueprint('map', __name__)

@map_bp.route('/')
def index():
    """World map view"""
    return render_template('index.html')

@map_bp.route('/map')
def map():
    """World map view"""
    return render_template('map.html')