from preprocessing.preprocessing import load_and_preprocess
from sklearn.svm import SVC
import joblib
import os
import sys
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


SAVED_MODELS_DIR = os.path.join(
    os.path.dirname(__file__), '..', '..', 'saved_models')


def train_svm(X_train=None, X_test=None, y_train=None, y_test=None):
    """
    Trains a Support Vector Machine (SVM) classifier.

    Args:
        X_train, X_test, y_train, y_test – optional pre-loaded data.

    Returns:
        model, X_test, y_test
    """

    print("\n" + "="*50)
    print("  TRAINING: Support Vector Machine (SVM)")
    print("="*50)

    if X_train is None:
        X_train, X_test, y_train, y_test, _, _ = load_and_preprocess(
            verbose=False)

    model = SVC(
        kernel='rbf',
        C=1.0,
        gamma='scale',
        probability=True,
        random_state=42
    )

    print("Training in progress …")
    model.fit(X_train, y_train)

    train_acc = model.score(X_train, y_train)
    test_acc = model.score(X_test,  y_test)
    print(f"  Train Accuracy : {train_acc:.4f}")
    print(f"  Test  Accuracy : {test_acc:.4f}")

    os.makedirs(SAVED_MODELS_DIR, exist_ok=True)
    save_path = os.path.join(SAVED_MODELS_DIR, 'svm.pkl')
    joblib.dump(model, save_path)
    print(f"  Model saved → {save_path}")

    return model, X_test, y_test


if __name__ == '__main__':
    train_svm()
    print("SVM training complete!")
