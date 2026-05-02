# =============================================================================
# train.py
# Purpose: Run the FULL training pipeline in one command.
#
# Steps:
#   1. Preprocess the dataset (clean, encode, split)
#   2. Calculate feature importance
#   3. Train all 4 models (Neural Network, kNN, Naive Bayes, SVM)
#   4. Evaluate all models and print comparison table
#
# Usage:
#   python train.py
# =============================================================================

import os
import sys
import time

# Make sure all submodules can be imported from project root
sys.path.insert(0, os.path.dirname(__file__))

from preprocessing.preprocessing           import load_and_preprocess
from features.features                      import calculate_feature_importance
from models.neural_network.neural_network   import train_neural_network
from models.knn.knn                         import train_knn
from models.naive_bayes.naive_bayes         import train_naive_bayes
from models.svm.svm                         import train_svm
from evaluation.evaluation                  import evaluate_all_models


def run_pipeline():
    print("\n" + "="*65)
    print("  ANIMAL CONDITION CLASSIFICATION SYSTEM - TRAINING PIPELINE")
    print("="*65)
    start_time = time.time()

    # ── STEP 1: Preprocessing ─────────────────────────────────────────────
    print("\n[Step 1/5]  Loading and preprocessing dataset …")
    X_train, X_test, y_train, y_test, encoders, df = load_and_preprocess(verbose=True)

    # ── STEP 2: Feature Importance ────────────────────────────────────────
    print("\n[Step 2/5]  Calculating feature importance …")
    calculate_feature_importance(X_train, y_train)

    # ── STEP 3: Train all models (pass data to avoid reloading) ──────────
    print("\n[Step 3/5]  Training all 4 models …")
    train_neural_network(X_train, X_test, y_train, y_test)
    train_knn           (X_train, X_test, y_train, y_test)
    train_naive_bayes   (X_train, X_test, y_train, y_test)
    train_svm           (X_train, X_test, y_train, y_test)

    # ── STEP 4: Evaluate all models ───────────────────────────────────────
    print("\n[Step 4/5]  Evaluating all models …")
    evaluate_all_models(X_test, y_test)

    # ── Done ──────────────────────────────────────────────────────────────
    elapsed = time.time() - start_time
    print("\n" + "="*65)
    print(f"  PIPELINE COMPLETE  ({elapsed:.1f}s)")
    print("  All models and results saved in:  saved_models/")
    print("  Run the API server with:          python main.py")
    print("="*65 + "\n")


if __name__ == '__main__':
    run_pipeline()
