from flask import Blueprint, render_template

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def index():
    """Dashboard home page"""
    return render_template('index.html')

@dashboard_bp.route('/dashboard')
def dashboard():
    """Dashboard view"""
    return render_template('dashboard.html')
