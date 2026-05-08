"""
utils.py — Shared utility functions for scrumIt
------------------------------------------------
These helpers are imported by routes, services, and analysis modules.
Each function is stubbed with a clear TODO so you know exactly what to fill in
once your data pipeline and ML model are defined.
"""

import os
import pickle
import logging
from datetime import datetime, date
from typing import Any

logger = logging.getLogger(__name__)


# ── 1. API RESPONSE HELPERS ───────────────────────────────────────────────────
# Consistent JSON shape for every API response.
# Frontend always receives: { success, data, error, meta }

def success_response(data: Any, meta: dict = None) -> dict:
    """
    Wrap a successful API result in a standard envelope.

    Usage:
        return jsonify(success_response({'confidence': 87.4})), 200

    Returns:
        {
            "success": true,
            "data": { ... },
            "meta": { "timestamp": "..." }
        }
    """
    return {
        'success': True,
        'data': data,
        'error': None,
        'meta': {
            'timestamp': datetime.utcnow().isoformat(),
            **(meta or {})
        }
    }


def error_response(message: str, code: str = 'UNKNOWN_ERROR') -> dict:
    """
    Wrap an error in a standard envelope.

    Usage:
        return jsonify(error_response('Invalid input', 'VALIDATION_ERROR')), 400

    Returns:
        {
            "success": false,
            "data": null,
            "error": { "message": "...", "code": "..." }
        }
    """
    return {
        'success': False,
        'data': None,
        'error': {
            'message': message,
            'code': code
        },
        'meta': {
            'timestamp': datetime.utcnow().isoformat()
        }
    }


# ── 2. DATA FORMATTING ────────────────────────────────────────────────────────
# Convert raw model output into clean values for the frontend.

def format_confidence(raw_score: float) -> dict:
    """
    Convert a raw model probability (0.0–1.0) into a display-ready dict.

    TODO: Adjust thresholds once you know what confidence ranges
          mean for your specific model.

    Args:
        raw_score: float between 0.0 and 1.0 from model.predict_proba()

    Returns:
        {
            "value": 87.4,       # percentage
            "label": "high",     # "high" / "medium" / "low"
            "display": "87.4%"   # ready to inject into HTML
        }
    """
    # TODO: adjust thresholds to match your model's output distribution
    percentage = round(float(raw_score) * 100, 1)

    if percentage >= 70:
        label = 'high'
    elif percentage >= 40:
        label = 'medium'
    else:
        label = 'low'

    return {
        'value': percentage,
        'label': label,
        'display': f'{percentage}%'
    }


def format_metric(value: float, unit: str = '', decimals: int = 1) -> str:
    """
    Format a numeric metric for display.

    Usage:
        format_metric(1234.5, unit='pts')  → "1,234.5 pts"
        format_metric(0.874, decimals=0)   → "1"

    TODO: Add currency formatting, K/M abbreviations, etc. as needed.
    """
    rounded = round(value, decimals)
    formatted = f'{rounded:,}'
    return f'{formatted} {unit}'.strip() if unit else formatted


def format_delta(current: float, previous: float) -> dict:
    """
    Compute the change between two values for display.

    Returns:
        {
            "value": 4.2,
            "display": "+4.2%",
            "direction": "up"   # "up" / "down" / "flat"
        }

    TODO: Decide whether delta should be absolute or percentage —
          update the calculation below to match your use case.
    """
    if previous == 0:
        delta = 0.0
    else:
        delta = round(((current - previous) / abs(previous)) * 100, 1)

    if delta > 0:
        direction, sign = 'up', '+'
    elif delta < 0:
        direction, sign = 'down', ''
    else:
        direction, sign = 'flat', ''

    return {
        'value': delta,
        'display': f'{sign}{delta}%',
        'direction': direction
    }


# ── 3. INPUT VALIDATION ───────────────────────────────────────────────────────
# Validate what the ML page sends before passing it to the model.

def validate_prediction_inputs(inputs: dict) -> tuple[bool, str]:
    """
    Check that the payload from POST /api/predict has everything the model needs.

    Usage:
        valid, message = validate_prediction_inputs(request.get_json())
        if not valid:
            return jsonify(error_response(message, 'VALIDATION_ERROR')), 400

    TODO: Replace REQUIRED_FIELDS with the actual field names your model expects.
          Add type checks and range validation for each field.

    Returns:
        (True, '')              if valid
        (False, 'reason...')    if invalid
    """
    # TODO: replace with your actual required input fields
    REQUIRED_FIELDS = [
        # 'team_size',
        # 'num_tickets',
        # 'sprint_length',
        # 'avg_complexity',
        # 'historical_velocity',
    ]

    if inputs is None:
        return False, 'Request body is missing or not valid JSON'

    for field in REQUIRED_FIELDS:
        if field not in inputs:
            return False, f'Missing required field: {field}'

    # TODO: add range validation, e.g.:
    # if not (1 <= inputs.get('team_size', 0) <= 50):
    #     return False, 'team_size must be between 1 and 50'

    return True, ''


def validate_numeric(value: Any, name: str, min_val: float = None, max_val: float = None) -> tuple[bool, str]:
    """
    Check that a single value is numeric and within an optional range.

    Usage:
        valid, msg = validate_numeric(inputs['team_size'], 'team_size', min_val=1, max_val=50)
    """
    try:
        num = float(value)
    except (TypeError, ValueError):
        return False, f'{name} must be a number'

    if min_val is not None and num < min_val:
        return False, f'{name} must be at least {min_val}'

    if max_val is not None and num > max_val:
        return False, f'{name} must be at most {max_val}'

    return True, ''

# ── 4. MODEL LOADING ──────────────────────────────────────────────────────────
# Safe model loading so the app doesn't crash if the file doesn't exist yet.

MODEL_PATH = os.path.join(
    os.path.dirname(__file__), '..', '..', 'data', 'processed', 'model.pkl'
)

def load_model(path: str = MODEL_PATH):
    """
    Load the trained model from disk.

    Usage (in prediction_service.py):
        model = load_model()
        if model is None:
            return error_response('Model not trained yet', 'MODEL_NOT_FOUND')

    Returns the model object if found, None if not.

    TODO: Update MODEL_PATH above to match where your model is saved.
          If you use multiple models, add a `model_name` argument.
    """
    resolved = os.path.abspath(path)
    if not os.path.exists(resolved):
        logger.warning(f'Model file not found at {resolved}. Train the model first.')
        return None

    try:
        with open(resolved, 'rb') as f:
            model = pickle.load(f)
        logger.info(f'Model loaded successfully from {resolved}')
        return model
    except Exception as e:
        logger.error(f'Failed to load model: {e}')
        return None


def model_is_ready(path: str = MODEL_PATH) -> bool:
    """
    Quick check — has the model been trained and saved yet?

    Usage:
        if not model_is_ready():
            return jsonify(error_response('Model not trained yet')), 503
    """
    return os.path.exists(os.path.abspath(path))


# ── 5. LOGGING HELPERS ────────────────────────────────────────────────────────

def log_prediction(inputs: dict, result: dict) -> None:
    """
    Log a prediction request and its result for debugging.

    TODO: Replace with proper structured logging or a database write
          once you want to track prediction history.
    """
    logger.info(f'Prediction | inputs={inputs} | result={result}')
