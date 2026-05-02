
import os
import sys
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import joblib
from sklearn.neural_network import MLPClassifier
from preprocessing.preprocessing import load_and_preprocess

SAVED_MODELS_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'saved_models')


def train_neural_network(X_train=None, X_test=None, y_train=None, y_test=None):
    """
    Trains a Multi-Layer Perceptron neural network classifier.

    Args:
        X_train, X_test, y_train, y_test – optional pre-loaded data.
            If None, data is loaded automatically.

    Returns:
        model   – the trained MLPClassifier
        X_test  – test feature array
        y_test  – test label array
    """

    print("\n" + "="*50)
    print("  TRAINING: Neural Network (MLP)")
    print("="*50)

    # ── Load data if not provided ──────────────────────────────────────────
    if X_train is None:
        X_train, X_test, y_train, y_test, _, _ = load_and_preprocess(verbose=False)

    # ──────────────────────────────────────────────────────────────────────
    # Build the Neural Network
    # ──────────────────────────────────────────────────────────────────────
    # hidden_layer_sizes=(64, 32)
    #   → Two hidden layers: first with 64 neurons, second with 32 neurons.
    #   → These numbers were chosen because:
    #       64 is large enough to capture complex symptom patterns.
    #       32 narrows down to extract the most relevant combinations.
    #
    # activation='relu'
    #   → ReLU (Rectified Linear Unit): output = max(0, x)
    #   → Most widely used activation. Avoids the "vanishing gradient" problem
    #     that occurs with sigmoid/tanh in deep networks.
    #
    # solver='adam'
    #   → Adam (Adaptive Moment Estimation) optimizer.
    #   → Automatically adjusts the learning rate during training.
    #   → Generally converges faster than plain SGD.
    #
    # max_iter=500
    #   → Maximum 500 passes over the training data (epochs).
    #   → Training stops early if the loss stops improving.
    #
    # random_state=42
    #   → Fixes the random seed so results are reproducible every run.
    # ──────────────────────────────────────────────────────────────────────
    model = MLPClassifier(
        hidden_layer_sizes=(64, 32),
        activation='relu',
        solver='adam',
        max_iter=500,
        random_state=42,
        early_stopping=True,      # Stop early if validation loss stops improving
        validation_fraction=0.1,  # Use 10% of training data for early-stopping check
        verbose=False
    )

    # ── Train the model ───────────────────────────────────────────────────
    print("Training in progress …")
    model.fit(X_train, y_train)

    # ── Quick accuracy check ──────────────────────────────────────────────
    train_acc = model.score(X_train, y_train)
    test_acc  = model.score(X_test,  y_test)
    print(f"  Train Accuracy : {train_acc:.4f}")
    print(f"  Test  Accuracy : {test_acc:.4f}")

    # ── Save model to disk ────────────────────────────────────────────────
    os.makedirs(SAVED_MODELS_DIR, exist_ok=True)
    save_path = os.path.join(SAVED_MODELS_DIR, 'neural_network.pkl')
    joblib.dump(model, save_path)
    print(f"  Model saved → {save_path}")

    return model, X_test, y_test


# Run directly:  python models/neural_network/neural_network.py
if __name__ == '__main__':
    train_neural_network()
    print("Neural Network training complete!")
