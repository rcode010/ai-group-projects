import pandas as pd
from sklearn.preprocessing import LabelEncoder


def load_data():
    df = pd.read_csv("data/dataset.csv")

    df = df.dropna()

    # convert text columns to numbers
    encoder = LabelEncoder()

    for col in df.columns:
        df[col] = encoder.fit_transform(df[col])

    X = df.iloc[:, :-1]
    y = df.iloc[:, -1]

    return X, y
