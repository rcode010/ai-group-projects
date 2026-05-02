import os
import joblib
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split


SAVED_MODELS_DIR = os.path.join(os.path.dirname(__file__), '..', 'saved_models')
DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'dataset.csv')


def load_and_preprocess(verbose=True):
    """
    Full preprocessing pipeline.

    Returns:
        X_train, X_test, y_train, y_test, encoders (dict), df (original DataFrame)
    """

    # ── Load ──────────────────────────────────────────────────────────────
    df = pd.read_csv(DATA_PATH)
    if verbose:
        print(f"  Loaded {len(df)} rows, {len(df.columns)} columns")

    # ── Clean ─────────────────────────────────────────────────────────────
    df = df.dropna()
    # Strip whitespace from string columns
    for col in df.select_dtypes(include='object').columns:
        df[col] = df[col].str.strip().str.lower()

    if verbose:
        print(f"  After cleaning: {len(df)} rows")

    # ── Encode ────────────────────────────────────────────────────────────
    encoders = {}      # one LabelEncoder per column (excluding target)
    feature_cols = [c for c in df.columns if c != 'Dangerous']

    for col in feature_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        encoders[col] = le

    # Encode target column
    target_le = LabelEncoder()
    df['Dangerous'] = target_le.fit_transform(df['Dangerous'])
    encoders['Dangerous'] = target_le

    # ── Build known values dict (for API autocomplete) ────────────────────
    known_values = {}
    for col in feature_cols:
        known_values[col] = list(encoders[col].classes_)

    # ── Split ─────────────────────────────────────────────────────────────
    X = df[feature_cols]
    y = df['Dangerous']
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    if verbose:
        print(f"  Train size: {len(X_train)},  Test size: {len(X_test)}")
        print(f"  Target distribution (train): {dict(y_train.value_counts())}")

    # ── Save encoders and known values ────────────────────────────────────
    os.makedirs(SAVED_MODELS_DIR, exist_ok=True)
    joblib.dump(encoders, os.path.join(SAVED_MODELS_DIR, 'encoders.pkl'))
    joblib.dump(known_values, os.path.join(SAVED_MODELS_DIR, 'known_values.pkl'))
    if verbose:
        print("  Encoders and known values saved.")

    return X_train, X_test, y_train, y_test, encoders, df


# Legacy alias so old imports still work
def load_data():
    X_train, X_test, y_train, y_test, _, df = load_and_preprocess(verbose=False)
    X = pd.concat([X_train, X_test])
    y = pd.concat([y_train, y_test])
    return X, y
