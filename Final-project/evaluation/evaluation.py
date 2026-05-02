import os
import sys
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import json
import joblib
import numpy  as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix, classification_report
)

from preprocessing.preprocessing import load_and_preprocess

SAVED_MODELS_DIR = os.path.join(os.path.dirname(__file__), '..', 'saved_models')


def evaluate_all_models(X_test=None, y_test=None):
    """
    Loads all saved models and evaluates them on the test set.
    Prints a comparison table and saves results to JSON.

    Returns:
        results_df – DataFrame with all metric scores per model
    """

    print("\n" + "="*65)
    print("  MODEL EVALUATION & COMPARISON")
    print("="*65)

    # ── Load test data if not provided ─────────────────────────────────────
    if X_test is None or y_test is None:
        _, X_test, _, y_test, _, _ = load_and_preprocess(verbose=False)

    # ── Model file map ─────────────────────────────────────────────────────
    model_files = {
        'Neural Network' : 'neural_network.pkl',
        'kNN'            : 'knn.pkl',
        'Naive Bayes'    : 'naive_bayes.pkl',
        'SVM'            : 'svm.pkl',
    }

    results = []  # Stores one dict per model

    for model_name, filename in model_files.items():
        path = os.path.join(SAVED_MODELS_DIR, filename)

        if not os.path.exists(path):
            print(f"  [WARNING] Model not found: {path}  (skipped)")
            continue

        # Load the model
        model = joblib.load(path)

        # Get predictions on the test set
        y_pred = model.predict(X_test)

        # Compute all four metrics
        acc  = accuracy_score (y_test, y_pred)
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec  = recall_score   (y_test, y_pred, zero_division=0)
        f1   = f1_score       (y_test, y_pred, zero_division=0)

        results.append({
            'Model'    : model_name,
            'Accuracy' : round(acc,  4),
            'Precision': round(prec, 4),
            'Recall'   : round(rec,  4),
            'F1-Score' : round(f1,   4),
        })

        # Print confusion matrix for each model
        cm = confusion_matrix(y_test, y_pred)
        print(f"\n--- {model_name} ---")
        print(f"  Accuracy : {acc:.4f}   Precision: {prec:.4f}")
        print(f"  Recall   : {rec:.4f}   F1-Score : {f1:.4f}")
        print(f"  Confusion Matrix:\n"
              f"               Pred: Not Dangerous   Pred: Dangerous\n"
              f"  Actual Not Dangerous  {cm[0,0]:>5}              {cm[0,1]:>5}\n"
              f"  Actual     Dangerous  {cm[1,0]:>5}              {cm[1,1]:>5}")

    # ── Comparison Table ───────────────────────────────────────────────────
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values('F1-Score', ascending=False).reset_index(drop=True)
    results_df['Rank'] = results_df.index + 1

    print("\n" + "="*65)
    print("  FINAL COMPARISON TABLE (sorted by F1-Score)")
    print("="*65)
    print(results_df[['Rank', 'Model', 'Accuracy', 'Precision', 'Recall', 'F1-Score']].to_string(index=False))

    # ── Rationale section ──────────────────────────────────────────────────
    _print_rationale(results_df)

    # ── Save results ───────────────────────────────────────────────────────
    os.makedirs(SAVED_MODELS_DIR, exist_ok=True)
    results_df.to_csv(os.path.join(SAVED_MODELS_DIR, 'evaluation_results.csv'), index=False)

    # Save as JSON for the Flask API to serve
    with open(os.path.join(SAVED_MODELS_DIR, 'evaluation_results.json'), 'w') as f:
        json.dump(results_df.to_dict(orient='records'), f, indent=2)

    # ── Plot comparison bar chart ──────────────────────────────────────────
    _plot_comparison(results_df, X_test, y_test, model_files)

    print(f"\n[Evaluation] Results saved to saved_models/evaluation_results.csv & .json")
    return results_df


def _print_rationale(results_df):
    """Prints a clear, professor-friendly explanation of why models perform differently."""

    print("\n" + "="*65)
    print("  RATIONALE: WHY EACH MODEL PERFORMS AS IT DOES")
    print("="*65)

    rationale = """
GENERAL CONTEXT:
  - Our features are ALL CATEGORICAL (animal name + 5 text symptoms).
  - The dataset has a CLASS IMBALANCE (likely more Not Dangerous than Dangerous).
  - All features are encoded as integers using LabelEncoder.

NEURAL NETWORK (MLP):
  + Can model complex, non-linear relationships between symptoms.
  + Two hidden layers (64→32 neurons) capture symptom interaction patterns.
  - Requires more data to generalise well. May underfit a small dataset.
  - Treats label-encoded integers as continuous → may misread category distances.
  → Expected: Good to excellent accuracy if data is large enough.

k-NEAREST NEIGHBORS (kNN):
  + Simple and intuitive — "similar animals have similar conditions."
  + No assumptions about data distribution.
  - Label-encoded integers make distance calculations approximate (not ideal
    for categorical data where "dog=1" and "cat=2" have no real distance).
  - Slow on large datasets (compares every new point to all training points).
  → Expected: Moderate performance; may overfit if k is too small.

NAIVE BAYES (CategoricalNB):
  + Purpose-built for CATEGORICAL data — best match for our dataset type.
  + Fast, handles class imbalance reasonably via prior probabilities.
  - Assumes ALL symptoms are INDEPENDENT of each other. In reality,
    symptoms like "fever" and "fatigue" often co-occur.
  → Expected: Strong baseline performance despite independence assumption.

SUPPORT VECTOR MACHINE (SVM):
  + Finds the optimal decision boundary (maximum margin hyperplane).
  + RBF kernel handles non-linear relationships effectively.
  + Robust to outliers (decision depends only on support vectors).
  - Sensitive to feature scale; label-encoded integers may cause issues
    if category values have large numeric gaps.
  - Slower training compared to Naive Bayes and kNN.
  → Expected: Good performance; often competitive with or better than NN
    on small-to-medium tabular datasets.

BEST MODEL SELECTION:
  - Use F1-Score as the primary metric (balances Precision and Recall).
  - In animal health classification, HIGH RECALL is critical:
    it is worse to miss a dangerous condition than to flag a safe one.
  - Whichever model achieves the highest F1-Score on the test set
    should be recommended as the production model.
"""
    print(rationale)


def _plot_comparison(results_df, X_test, y_test, model_files):
    """Creates a grouped bar chart comparing all model metrics."""

    metrics = ['Accuracy', 'Precision', 'Recall', 'F1-Score']
    x = np.arange(len(results_df))
    width = 0.2

    fig, ax = plt.subplots(figsize=(12, 6))
    colors = ['#4C72B0', '#DD8452', '#55A868', '#C44E52']

    for i, metric in enumerate(metrics):
        ax.bar(x + i * width, results_df[metric], width,
               label=metric, color=colors[i], alpha=0.85)

    ax.set_xlabel('Model')
    ax.set_ylabel('Score')
    ax.set_title('Model Comparison — Accuracy / Precision / Recall / F1-Score')
    ax.set_xticks(x + width * 1.5)
    ax.set_xticklabels(results_df['Model'])
    ax.set_ylim(0, 1.1)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plot_path = os.path.join(SAVED_MODELS_DIR, 'model_comparison.png')
    plt.savefig(plot_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"[Evaluation] Comparison chart saved → {plot_path}")

    # ── Confusion matrix grid ──────────────────────────────────────────────
    fig2, axes = plt.subplots(2, 2, figsize=(10, 8))
    axes = axes.flatten()
    model_list = list(model_files.items())

    for idx, (model_name, filename) in enumerate(model_list):
        path = os.path.join(SAVED_MODELS_DIR, filename)
        if not os.path.exists(path):
            continue
        model  = joblib.load(path)
        y_pred = model.predict(X_test)
        cm     = confusion_matrix(y_test, y_pred)
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[idx],
                    xticklabels=['Not Dangerous', 'Dangerous'],
                    yticklabels=['Not Dangerous', 'Dangerous'])
        axes[idx].set_title(model_name)
        axes[idx].set_xlabel('Predicted')
        axes[idx].set_ylabel('Actual')

    plt.suptitle('Confusion Matrices — All Models', fontsize=13, fontweight='bold')
    plt.tight_layout()
    cm_path = os.path.join(SAVED_MODELS_DIR, 'confusion_matrices.png')
    plt.savefig(cm_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"[Evaluation] Confusion matrices saved → {cm_path}")


# Run directly:  python evaluation/evaluation.py
if __name__ == '__main__':
    evaluate_all_models()
