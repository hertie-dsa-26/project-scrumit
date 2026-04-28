from flask import Blueprint, jsonify, request
from app.services.prediction_service import MoneyLaunderingPredictor

api_bp = Blueprint('api', __name__, url_prefix='/api')

# Initialize predictor once
_predictor = None

def get_predictor():
    """Lazy-load predictor singleton"""
    global _predictor
    if _predictor is None:
        _predictor = MoneyLaunderingPredictor()
    return _predictor

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    predictor = get_predictor()
    return jsonify({
        'status': 'healthy',
        'service': 'scrumIt ML Dashboard',
        'preprocessor_available': predictor.preprocessor_available
    }), 200

@api_bp.route('/predict', methods=['POST'])
def predict():
    """
    ML prediction endpoint for money laundering detection.
    
    Request body:
    {
        'from_bank': str,
        'account': str,
        'to_bank': str,
        'account.1': str,
        'amount_received': float,
        'receiving_currency': str,
        'amount_paid': float,
        'payment_currency': str,
        'currency_mismatch': str,
        'payment_format': str,
        's_country': str,
        'r_country': str,
        's_bank_type': str,
        'r_bank_type': str
    }
    """
    try:
        predictor = get_predictor()
        
        # Check if preprocessing is available
        if not predictor.preprocessor_available:
            return jsonify({
                'success': False,
                'error': 'Preprocessing pipeline not available. '
                        'This Flask instance requires Python 3.11 with PyCaret.'
            }), 503
        
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Make prediction
        result = predictor.predict(data)
        
        return jsonify({
            'success': True,
            'is_laundering': result['is_laundering'],
            'probability': result['probability'],
            'confidence': result['confidence'],
            'message': f"Transaction has {result['probability']*100:.1f}% probability of being money laundering"
        }), 200
        
    except ValueError as e:
        # Missing or invalid features
        return jsonify({
            'success': False,
            'error': f'Invalid input: {str(e)}'
        }), 400
    
    except RuntimeError as e:
        # Preprocessing not available
        return jsonify({
            'success': False,
            'error': str(e)
        }), 503
    
    except Exception as e:
        # Unexpected error
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Prediction error: {str(e)}'
        }), 500

@api_bp.route('/required-features', methods=['GET'])
def required_features():
    """
    Return list of required features for prediction.
    """
    required_fields = {
        'categorical': [
            'from_bank', 'account', 'to_bank', 'account.1',
            'receiving_currency', 'payment_currency', 'currency_mismatch',
            'payment_format', 's_country', 'r_country', 's_bank_type', 'r_bank_type'
        ],
        'numerical': ['amount_received', 'amount_paid'],
        'preprocessor_available': get_predictor().preprocessor_available
    }
    return jsonify(required_fields), 200
