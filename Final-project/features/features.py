# =============================================================================
# features.py
# Purpose: Calculate and explain HOW IMPORTANT each feature (symptom / animal
#          name) is when predicting whether a condition is Dangerous or not.
#
# Two methods are used:
#   1. Chi-Squared Test  – measures statistical relationship between each
#                          categorical feature and the target label.
#   2. Random Forest     – measures how much each feature reduces prediction
#                          error inside a forest of decision trees.
# =============================================================================

import os
import sys
import warnings
warnings.filterwarnings('ignore')

# Add project root to path so we can import preprocessing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pandas as pd
import numpy as np
import joblib
import matplotlib
matplotlib.use('Agg')          # Non-interactive backend (safe for all environments)
import matplotlib.pyplot as plt
from sklearn.feature_selection import chi2
from sklearn.ensemble import RandomForestClassifier

from preprocessing.preprocessing import load_and_preprocess

SAVED_MODELS_DIR = os.path.join(os.path.dirname(__file__), '..', 'saved_models')
FEATURE_NAMES    = ['AnimalName', 'symptoms1', 'symptoms2', 'symptoms3', 'symptoms4', 'symptoms5']


def calculate_feature_importance(X_train=None, y_train=None):
    """
    Calculates feature importance using two methods and saves the results.

    Args:
        X_train, y_train – optional pre-loaded data. If None, data is loaded
                           automatically via load_and_preprocess().

    Returns:
        importance_df – a DataFrame ranking features by Chi2 score.
    """

    # ── Load data if not provided ──────────────────────────────────────────
    if X_train is None or y_train is None:
        X_train, _, y_train, _, _, _ = load_and_preprocess(verbose=False)

    print("\n" + "="*60)
    print("  FEATURE IMPORTANCE ANALYSIS")
    print("="*60)

    # ──────────────────────────────────────────────────────────────────────
    # METHOD 1: Chi-Squared Test
    # ──────────────────────────────────────────────────────────────────────
    # WHY chi2?
    #   All our features are categorical (text encoded as integers).
    #   Chi-squared measures whether a feature and the target are
    #   statistically INDEPENDENT or RELATED.
    #   → High score = strong relationship → feature is important.
    #   → Low  score = weak  relationship → feature adds little information.
    #
    # p-value interpretation:
    #   p < 0.05  → the relationship is statistically significant (reliable)
    #   p ≥ 0.05  → the relationship may be due to chance
    # ──────────────────────────────────────────────────────────────────────
    chi2_scores, p_values = chi2(X_train, y_train)

    # ──────────────────────────────────────────────────────────────────────
    # METHOD 2: Random Forest Feature Importance (Gini Impurity)
    # ──────────────────────────────────────────────────────────────────────
    # A Random Forest is an ensemble of decision trees.
    # Each tree splits on features that best separate Dangerous vs Not Dangerous.
    # Feature importance = average reduction in "Gini impurity" caused by
    #   that feature across all trees.
    # → Higher importance = feature contributes more to correct predictions.
    # ──────────────────────────────────────────────────────────────────────
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)
    rf_importances = rf.feature_importances_

    # ── Build summary table ────────────────────────────────────────────────
    importance_df = pd.DataFrame({
        'Feature'       : FEATURE_NAMES,
        'Chi2_Score'    : np.round(chi2_scores, 4),
        'P_Value'       : np.round(p_values, 4),
        'RF_Importance' : np.round(rf_importances, 4),
    }).sort_values('Chi2_Score', ascending=False).reset_index(drop=True)

    importance_df['Rank'] = importance_df.index + 1

    print(importance_df[['Rank', 'Feature', 'Chi2_Score', 'P_Value', 'RF_Importance']].to_string(index=False))
    print()
    print("KEY:")
    print("  Chi2_Score   : Higher = more important (stronger link to target)")
    print("  P_Value      : Lower  = more statistically reliable (< 0.05 is good)")
    print("  RF_Importance: Higher = feature reduces more prediction uncertainty")

    # ── Save results ──────────────────────────────────────────────────────
    os.makedirs(SAVED_MODELS_DIR, exist_ok=True)
    importance_df.to_csv(os.path.join(SAVED_MODELS_DIR, 'feature_importance.csv'), index=False)
    joblib.dump(importance_df.to_dict(orient='records'),
                os.path.join(SAVED_MODELS_DIR, 'feature_importance.pkl'))

    # ── Plot ──────────────────────────────────────────────────────────────
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle('Feature Importance Analysis', fontsize=14, fontweight='bold')

    # Chi2 bar chart
    axes[0].barh(importance_df['Feature'][::-1], importance_df['Chi2_Score'][::-1],
                 color='steelblue', edgecolor='white')
    axes[0].set_title('Chi-Squared Score')
    axes[0].set_xlabel('Chi2 Score  (higher = more important)')
    axes[0].set_xlim(left=0)

    # Random Forest bar chart
    rf_sorted = importance_df.sort_values('RF_Importance', ascending=True)
    axes[1].barh(rf_sorted['Feature'], rf_sorted['RF_Importance'],
                 color='coral', edgecolor='white')
    axes[1].set_title('Random Forest Importance')
    axes[1].set_xlabel('Importance Score  (higher = more important)')
    axes[1].set_xlim(left=0)

    plt.tight_layout()
    plot_path = os.path.join(SAVED_MODELS_DIR, 'feature_importance.png')
    plt.savefig(plot_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"\n[Features] Plot saved → {plot_path}")

    return importance_df


# Run directly:  python features/features.py
if __name__ == '__main__':
    calculate_feature_importance()
