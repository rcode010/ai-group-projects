import os
import sys
import json
import joblib
import numpy as np

from flask import Flask, request, jsonify
from flask_cors import CORS     # Allows the React frontend (different port) to call this API

# Add project root to Python path
sys.path.insert(0, os.path.dirname(__file__))

# ── App setup ─────────────────────────────────────────────────────────────────
app = Flask(__name__)
CORS(app)   # Enable Cross-Origin Resource Sharing for all routes

SAVED_MODELS_DIR = os.path.join(os.path.dirname(__file__), 'saved_models')

# ── Global variables for loaded models and encoders ───────────────────────────
MODELS   = {}      # { 'neural_network': <model>, 'knn': <model>, ... }
ENCODERS = {}      # { 'AnimalName': <LabelEncoder>, 'symptoms1': ... }
KNOWN_VALUES = {}  # { 'AnimalName': ['cat','dog',...], 'symptoms1': [...], ... }

FEATURE_COLS = ['AnimalName', 'symptoms1', 'symptoms2', 'symptoms3', 'symptoms4', 'symptoms5']


# =============================================================================
# STARTUP: Load everything from disk when the server starts
# =============================================================================
def load_all():
    """Load all models, encoders, and known values from the saved_models folder."""

    global MODELS, ENCODERS, KNOWN_VALUES

    # ── Load encoders ────────────────────────────────────────────────────────
    enc_path = os.path.join(SAVED_MODELS_DIR, 'encoders.pkl')
    if not os.path.exists(enc_path):
        print("[WARNING] encoders.pkl not found. Run 'python train.py' first.")
        return False
    ENCODERS = joblib.load(enc_path)

    # ── Load known values (for autocomplete) ─────────────────────────────────
    kv_path = os.path.join(SAVED_MODELS_DIR, 'known_values.pkl')
    if os.path.exists(kv_path):
        KNOWN_VALUES = joblib.load(kv_path)

    # ── Load models ───────────────────────────────────────────────────────────
    model_files = {
        'neural_network' : 'neural_network.pkl',
        'knn'            : 'knn.pkl',
        'naive_bayes'    : 'naive_bayes.pkl',
        'svm'            : 'svm.pkl',
    }

    for name, filename in model_files.items():
        path = os.path.join(SAVED_MODELS_DIR, filename)
        if os.path.exists(path):
            MODELS[name] = joblib.load(path)
            print(f"  [Loaded] {name}")
        else:
            print(f"  [Missing] {name} — run train.py first")

    return len(MODELS) > 0


# =============================================================================
# HELPER: Encode a single user input row into the numeric format models expect
# =============================================================================
def encode_input(animal_name, symptoms):
    """
    Encodes one user input using the saved LabelEncoders.

    Args:
        animal_name  – string, e.g. "dog"
        symptoms     – list of 5 strings, e.g. ["fever", "vomiting", ...]

    Returns:
        np.array of shape (1, 6)  — ready for model.predict()

    Raises:
        ValueError with a helpful message if an unknown value is entered.
    """
    values = [animal_name.lower().strip()] + [s.lower().strip() for s in symptoms]
    encoded = []

    for col, value in zip(FEATURE_COLS, values):
        le = ENCODERS[col]
        # Check if the value was seen during training
        if value not in le.classes_:
            # If the user types a random unknown symptom, we don't want to crash.
            # We assign it a default encoded value (0) so the models can still
            # process the input and provide a prediction based on the other known symptoms.
            encoded.append(0)
        else:
            encoded.append(le.transform([value])[0])

    return np.array(encoded).reshape(1, -1)


# =============================================================================
# ROUTES
# =============================================================================

@app.route('/health', methods=['GET'])
def health():
    """Simple health check — confirms the server is running."""
    return jsonify({
        'status'       : 'ok',
        'models_loaded': list(MODELS.keys()),
    })


@app.route('/metadata', methods=['GET'])
def metadata():
    """
    Returns the list of known animal names and symptom values.
    The React frontend uses this to power the autocomplete suggestions.
    """
    return jsonify(KNOWN_VALUES)


@app.route('/feature-importance', methods=['GET'])
def feature_importance():
    """Returns the feature importance data calculated during training."""
    path = os.path.join(SAVED_MODELS_DIR, 'feature_importance.pkl')
    if not os.path.exists(path):
        return jsonify({'error': 'Feature importance not found. Run train.py first.'}), 404
    data = joblib.load(path)
    return jsonify(data)


@app.route('/evaluation', methods=['GET'])
def evaluation():
    """Returns model evaluation metrics (accuracy, precision, recall, F1)."""
    path = os.path.join(SAVED_MODELS_DIR, 'evaluation_results.json')
    if not os.path.exists(path):
        return jsonify({'error': 'Evaluation results not found. Run train.py first.'}), 404
    with open(path, 'r') as f:
        data = json.load(f)
    return jsonify(data)


@app.route('/predict', methods=['POST'])
def predict():
    """
    Main prediction endpoint.

    Expects JSON body:
    {
        "animal_name" : "dog",
        "symptom1"    : "fever",
        "symptom2"    : "vomiting",
        "symptom3"    : "lethargy",
        "symptom4"    : "loss of appetite",
        "symptom5"    : "coughing"
    }

    Returns:
    {
        "predictions": {
            "neural_network": { "label": "Dangerous",     "confidence": 0.87 },
            "knn"           : { "label": "Not Dangerous", "confidence": 0.60 },
            "naive_bayes"   : { "label": "Dangerous",     "confidence": 0.92 },
            "svm"           : { "label": "Dangerous",     "confidence": 0.81 }
        }
    }
    """
    if not MODELS:
        return jsonify({'error': 'No models loaded. Run python train.py first.'}), 503

    # ── Parse request body ────────────────────────────────────────────────
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body must be JSON.'}), 400

    animal_name = data.get('animal_name', '').strip()
    symptoms    = [
        data.get('symptom1', '').strip(),
        data.get('symptom2', '').strip(),
        data.get('symptom3', '').strip(),
        data.get('symptom4', '').strip(),
        data.get('symptom5', '').strip(),
    ]

    # Validate that all fields are filled
    if not animal_name or any(s == '' for s in symptoms):
        return jsonify({'error': 'Please fill in the animal name and all 5 symptoms.'}), 400

    # ── Encode input ──────────────────────────────────────────────────────
    try:
        X = encode_input(animal_name, symptoms)
    except ValueError as e:
        return jsonify({'error': str(e)}), 422

    # ── Run all models ────────────────────────────────────────────────────
    predictions = {}

    for model_name, model in MODELS.items():
        # Get predicted class: 1 = Dangerous, 0 = Not Dangerous
        pred_class = int(model.predict(X)[0])

        # Get confidence (probability) if supported
        try:
            proba       = model.predict_proba(X)[0]
            # proba[1] = probability of class 1 (Dangerous)
            # proba[0] = probability of class 0 (Not Dangerous)
            confidence  = float(proba[pred_class])
        except Exception:
            confidence = 1.0 if pred_class == 1 else 0.0

        predictions[model_name] = {
            'label'     : 'Dangerous' if pred_class == 1 else 'Not Dangerous',
            'confidence': round(confidence * 100, 1),   # as a percentage
            'raw_class' : pred_class,
        }

    return jsonify({
        'animal_name': animal_name,
        'symptoms'   : symptoms,
        'predictions': predictions,
    })


# =============================================================================
# ENTRY POINT
# =============================================================================
if __name__ == '__main__':
    print("\n" + "="*55)
    print("  Animal Condition Classification — API Server")
    print("="*55)
    print("Loading models …")

    ok = load_all()

    if not ok:
        print("\n[ERROR] Could not load models.")
        print("  Please run:  python train.py")
        print("  Then start the server again.\n")
    else:
        print(f"\n  {len(MODELS)} model(s) loaded successfully.")
        print("  Starting server on  http://localhost:5000")
        print("  Press Ctrl+C to stop.\n")
        # debug=False for stability; host='0.0.0.0' to allow LAN access
        app.run(host='0.0.0.0', port=5000, debug=False)
