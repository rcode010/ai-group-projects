from models.svm.svm import train_svm
from preprocessing.preprocessing import load_data
from sklearn.model_selection import train_test_split
from models.knn.knn import train_knn

# 1. Load data
X, y = load_data()

# 2. Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 3. Train kNN
results = train_knn(X_train, X_test, y_train, y_test)

# 4. Print result
print(results)


svm_results = train_svm(X_train, X_test, y_train, y_test)

print("SVM Results:")
print(svm_results)
