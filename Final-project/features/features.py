import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier

def run_feature_analysis(X, y):
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    
    importance_df = pd.DataFrame({
        'Feature': X.columns,
        'Importance': model.feature_importances_
    }).sort_values(by='Importance', ascending=False)

    plt.figure(figsize=(10, 6))
    sns.barplot(x='Importance', y='Feature', data=importance_df, palette='viridis')
    plt.title('Feature Importance')
    plt.tight_layout()
    plt.savefig('features/feature_importance.png')
    plt.show()

    best_features = importance_df['Feature'].head(5).tolist()
    worst_features = importance_df['Feature'].tail(3).tolist()
    
    return best_features, worst_features

if __name__ == "__main__":
    pass