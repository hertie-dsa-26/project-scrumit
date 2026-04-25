from flask import Blueprint, render_template

ml_bp = Blueprint('ml', __name__)

@ml_bp.route('/ml')
def ml_view():
    """ML interactive page"""
    return render_template('ml.html')
