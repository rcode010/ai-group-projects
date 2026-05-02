import os
import sys
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import joblib
from sklearn.naive_bayes import GaussianNB
from preprocessing.preprocessing import load_and_preprocess

SAVED_MODELS_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'saved_models')


def train_naive_bayes(X_train=None, X_test=None, y_train=None, y_test=None):
    """
    Trains a Gaussian Naive Bayes classifier.

    Args:
        X_train, X_test, y_train, y_test - optional pre-loaded data.

    Returns:
        model, X_test, y_test
    """

    print("\n" + "="*50)
    print("  TRAINING: Naive Bayes (GaussianNB)")
    print("="*50)

    # -- Load data if not provided -------------------------------------------
    if X_train is None:
        X_train, X_test, y_train, y_test, _, _ = load_and_preprocess(verbose=False)

    # -------------------------------------------------------------------------
    # Build the Gaussian Naive Bayes Classifier
    # -------------------------------------------------------------------------
    # GaussianNB assumes each feature follows a Gaussian (normal) distribution
    # within each class. For each class it estimates the mean and variance of
    # every feature, then uses those to compute likelihoods at prediction time.
    # var_smoothing adds a small fraction of the largest variance to all
    # variances, improving stability when a feature has very low variance.
    # -------------------------------------------------------------------------
    model = GaussianNB(var_smoothing=1e-9)

    # -- Train the model ---------------------------------------------------
    print("Training in progress ...")
    model.fit(X_train, y_train)

    # -- Quick accuracy check ----------------------------------------------
    train_acc = model.score(X_train, y_train)
    test_acc  = model.score(X_test,  y_test)
    print(f"  Train Accuracy : {train_acc:.4f}")
    print(f"  Test  Accuracy : {test_acc:.4f}")

    # -- Save model to disk ------------------------------------------------
    os.makedirs(SAVED_MODELS_DIR, exist_ok=True)
    save_path = os.path.join(SAVED_MODELS_DIR, 'naive_bayes.pkl')
    joblib.dump(model, save_path)
    print(f"  Model saved -> {save_path}")

    return model, X_test, y_test


# Run directly:  python models/naive_bayes/naive_bayes.py
if __name__ == '__main__':
    train_naive_bayes()
    print("Naive Bayes training complete!")

