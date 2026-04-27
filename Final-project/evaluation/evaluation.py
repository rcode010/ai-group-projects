

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)


def evaluate_model(model_name, y_true, y_pred):
  

    results = {
        "Model": model_name,
        "Accuracy": round(accuracy_score(y_true, y_pred), 4),
        "Precision": round(precision_score(y_true, y_pred), 4),
        "Recall": round(recall_score(y_true, y_pred), 4),
        "F1 Score": round(f1_score(y_true, y_pred), 4)
    }

    return results


def compare_models(results_list):


    df = pd.DataFrame(results_list)

    print("\n========== MODEL COMPARISON ==========\n")
    print(df.to_string(index=False))

    return df



def plot_comparison_chart(df):

    df_plot = df.set_index("Model")

    df_plot.plot(
        kind="bar",
        figsize=(10, 6)
    )

    plt.title("Model Performance Comparison")
    plt.ylabel("Score")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.show()



def plot_confusion_matrix(y_true, y_pred, model_name):

    cm = confusion_matrix(y_true, y_pred)

    plt.figure(figsize=(5, 4))

    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues"
    )

    plt.title(f"{model_name} Confusion Matrix")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.tight_layout()
    plt.show()



def explain_results(df):

    print("\n========== ANALYSIS ==========\n")

    best_model = df.loc[df["Accuracy"].idxmax(), "Model"]
    best_score = df["Accuracy"].max()

    print(f"Best performing model: {best_model} ({best_score})\n")

    for _, row in df.iterrows():

        model = row["Model"]

        if model.lower() == "svm":
            print("- SVM performed well because it handles class separation effectively.")

        elif model.lower() == "knn":
            print("- kNN performance depends on nearest neighbors and feature scaling.")

        elif model.lower() == "naive bayes":
            print("- Naive Bayes is efficient but assumes independent features.")

        elif model.lower() == "neural network":
            print("- Neural Network captures complex relationships but may require tuning.")

        else:
            print(f"- {model} performance reviewed.")



def run_evaluation(predictions):


    all_results = []

    for model_name, (y_true, y_pred) in predictions.items():

        result = evaluate_model(model_name, y_true, y_pred)
        all_results.append(result)

    # Comparison table
    df = compare_models(all_results)

    # Bar chart
    plot_comparison_chart(df)

    # Confusion matrices
    for model_name, (y_true, y_pred) in predictions.items():
        plot_confusion_matrix(y_true, y_pred, model_name)

    # Analysis
    explain_results(df)

    return df