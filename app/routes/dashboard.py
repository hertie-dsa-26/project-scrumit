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