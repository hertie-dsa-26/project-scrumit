from flask import Blueprint, jsonify

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'scrumIt ML Dashboard'
    }), 200

@api_bp.route('/predict', methods=['POST'])
def predict():
    """ML prediction endpoint"""
    return jsonify({'message': 'Prediction endpoint'}), 200
