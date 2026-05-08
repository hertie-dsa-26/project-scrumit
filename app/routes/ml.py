from flask import Blueprint, render_template

ml_bp = Blueprint('ml', __name__)


@ml_bp.route('/ml')
def ml_dashboard():
	"""ML dashboard view."""
	return render_template('ml.html')


@ml_bp.route('/how-our-model-works')
def model_explanation():
	"""Model explanation and documentation page."""
	return render_template('model-explanation.html')
