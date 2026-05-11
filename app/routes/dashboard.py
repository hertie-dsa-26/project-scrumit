from flask import Blueprint, render_template
import json
from pathlib import Path

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def index():
    return render_template('index.html')

@dashboard_bp.route('/dashboard')
def dashboard():
    root = Path(__file__).parent.parent.parent
    with open(root / 'app/static/charts/overview.json') as f:
        overview = json.load(f)
    return render_template('dashboard.html', **overview)

@dashboard_bp.route('/meet-the-team')
def meet_the_team():
    return render_template('meet_the_team.html')

@dashboard_bp.route('/about-data')
def about_data():
    return render_template('about_data.html')