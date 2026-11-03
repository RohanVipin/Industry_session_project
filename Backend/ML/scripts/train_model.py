

import pandas as pd
import os

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    classification_report
)


# =========================================================
# 1. LOAD PROCESSED DATA
# =========================================================

base_path = os.path.dirname(os.path.dirname(__file__))

data_path = os.path.join(
    base_path,
    "datasets",
    "processed_data.csv"
)

df = pd.read_csv(data_path)

print("Dataset shape:", df.shape)


# =========================================================
# 2. SEPARATE FEATURES AND TARGET
# =========================================================

X = df.drop(columns=["churn"])

y = df["churn"]


print("\nFeatures:", X.shape)
print("Target:", y.shape)


# =========================================================
# 3. IDENTIFY CATEGORICAL AND NUMERICAL FEATURES
# =========================================================

categorical_features = X.select_dtypes(
    include=["object"]
).columns.tolist()

numerical_features = X.select_dtypes(
    include=["int64", "float64"]
).columns.tolist()


print("\nCategorical features:")
print(categorical_features)

print("\nNumerical features:")
print(numerical_features)


# =========================================================
# 4. TRAIN / TEST SPLIT
# =========================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


print("\nTraining samples:", X_train.shape[0])
print("Testing samples:", X_test.shape[0])


# =========================================================
# 5. PREPROCESSING
# =========================================================

preprocessor = ColumnTransformer(

    transformers=[

        (
            "categorical",
            OneHotEncoder(
                handle_unknown="ignore"
            ),
            categorical_features
        ),

        (
            "numerical",
            StandardScaler(),
            numerical_features
        )

    ]
)


# =========================================================
# 6. LOGISTIC REGRESSION
# =========================================================

logistic_model = Pipeline(

    steps=[

        (
            "preprocessor",
            preprocessor
        ),

        (
            "classifier",
            LogisticRegression(
                max_iter=1000,
                class_weight="balanced"
            )
        )

    ]
)


print("\n========== LOGISTIC REGRESSION ==========")

logistic_model.fit(
    X_train,
    y_train
)

logistic_predictions = logistic_model.predict(
    X_test
)

logistic_probabilities = logistic_model.predict_proba(
    X_test
)[:, 1]


print(
    classification_report(
        y_test,
        logistic_predictions
    )
)

print(
    "Accuracy:",
    accuracy_score(
        y_test,
        logistic_predictions
    )
)

print(
    "Precision:",
    precision_score(
        y_test,
        logistic_predictions
    )
)

print(
    "Recall:",
    recall_score(
        y_test,
        logistic_predictions
    )
)

print(
    "F1 Score:",
    f1_score(
        y_test,
        logistic_predictions
    )
)

print(
    "ROC-AUC:",
    roc_auc_score(
        y_test,
        logistic_probabilities
    )
)


# =========================================================
# 7. RANDOM FOREST
# =========================================================

random_forest_model = Pipeline(

    steps=[

        (
            "preprocessor",
            preprocessor
        ),

        (
            "classifier",
            RandomForestClassifier(
                n_estimators=200,
                random_state=42,
                class_weight="balanced",
                n_jobs=-1
            )
        )

    ]
)


print("\n========== RANDOM FOREST ==========")

random_forest_model.fit(
    X_train,
    y_train
)

rf_predictions = random_forest_model.predict(
    X_test
)

rf_probabilities = random_forest_model.predict_proba(
    X_test
)[:, 1]


print(
    classification_report(
        y_test,
        rf_predictions
    )
)

print(
    "Accuracy:",
    accuracy_score(
        y_test,
        rf_predictions
    )
)

print(
    "Precision:",
    precision_score(
        y_test,
        rf_predictions
    )
)

print(
    "Recall:",
    recall_score(
        y_test,
        rf_predictions
    )
)

print(
    "F1 Score:",
    f1_score(
        y_test,
        rf_predictions
    )
)

print(
    "ROC-AUC:",
    roc_auc_score(
        y_test,
        rf_probabilities
    )
)


# =========================================================
# 7b. XGBOOST
# =========================================================

# The data is imbalanced (~9.7% churn). scale_pos_weight plays the same
# role as class_weight="balanced" in the other two models.
# Hyperparameters were chosen by 5-fold cross-validation on the TRAINING
# split only (the test split was not used for tuning).
scale_pos_weight = (y_train == 0).sum() / (y_train == 1).sum()

xgboost_model = Pipeline(

    steps=[

        (
            "preprocessor",
            preprocessor
        ),

        (
            "classifier",
            XGBClassifier(
                n_estimators=400,
                learning_rate=0.03,
                max_depth=5,
                min_child_weight=5,
                subsample=0.8,
                colsample_bytree=0.8,
                scale_pos_weight=scale_pos_weight,
                eval_metric="logloss",
                random_state=42,
                n_jobs=-1
            )
        )

    ]
)


print("\n========== XGBOOST ==========")

xgboost_model.fit(
    X_train,
    y_train
)

xgb_predictions = xgboost_model.predict(
    X_test
)

xgb_probabilities = xgboost_model.predict_proba(
    X_test
)[:, 1]


print(
    classification_report(
        y_test,
        xgb_predictions
    )
)

print("Accuracy:", accuracy_score(y_test, xgb_predictions))
print("Precision:", precision_score(y_test, xgb_predictions))
print("Recall:", recall_score(y_test, xgb_predictions))
print("F1 Score:", f1_score(y_test, xgb_predictions))
print("ROC-AUC:", roc_auc_score(y_test, xgb_probabilities))


# =========================================================
# 8. MODEL COMPARISON
# =========================================================

candidates = {

    "Logistic Regression": (logistic_model, logistic_predictions, logistic_probabilities),
    "Random Forest":       (random_forest_model, rf_predictions, rf_probabilities),
    "XGBoost":             (xgboost_model, xgb_predictions, xgb_probabilities)

}

print("\n==========================================")
print("             MODEL COMPARISON")
print("==========================================")

print(f"{'Model':<22}{'F1':>8}{'Precision':>11}{'Recall':>9}{'ROC-AUC':>9}{'PR-AUC':>8}")

scores = {}

for name, (_, preds, probs) in candidates.items():

    scores[name] = f1_score(y_test, preds)

    print(
        f"{name:<22}"
        f"{f1_score(y_test, preds):>8.4f}"
        f"{precision_score(y_test, preds):>11.4f}"
        f"{recall_score(y_test, preds):>9.4f}"
        f"{roc_auc_score(y_test, probs):>9.4f}"
        f"{average_precision_score(y_test, probs):>8.4f}"
    )


# Best model = highest F1 score (same rule as the original script)
best_name = max(scores, key=scores.get)

best_model = candidates[best_name][0]

print(f"\nBest Model: {best_name}")


# =========================================================
# 9. SAVE BEST MODEL
# =========================================================

import joblib

models_path = os.path.join(
    base_path,
    "models"
)

os.makedirs(
    models_path,
    exist_ok=True
)

model_path = os.path.join(
    models_path,
    "churn_model.pkl"
)

joblib.dump(
    best_model,
    model_path
)


print(
    "\nBest model saved at:"
)

print(model_path)

print(
    "\n========== MODEL TRAINING COMPLETED =========="
)

