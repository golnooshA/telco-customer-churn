# pipeline.py
import os
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import joblib

df = pd.read_csv("data/telco_customer_churn.csv")

df["TotalCharges"] = pd.to_numeric(df["TotalCharges"].astype(str).str.strip(), errors="coerce")

mask_na = df["TotalCharges"].isna()
df.loc[mask_na & (df["tenure"] == 0), "TotalCharges"] = 0

df["TotalCharges"] = df["TotalCharges"].fillna(df["MonthlyCharges"] * df["tenure"])
df["TotalCharges"] = df["TotalCharges"].fillna(df["TotalCharges"].median())

df["Churn"] = df["Churn"].map({"No": 0, "Yes": 1}).astype(int)

customer_ids = df["customerID"].copy()


X = df.drop(columns=["Churn", "customerID"])
y = df["Churn"]

num_cols = X.select_dtypes(include=["int64", "float64"]).columns.tolist()
cat_cols = X.select_dtypes(include=["object", "bool", "category"]).columns.tolist()

print("Shapes -> X:", X.shape, "| y:", y.shape)
print("Numeric cols:", num_cols)
print("Categorical cols:", cat_cols)


X_train, X_test, y_train, y_test, id_train, id_test = train_test_split(
    X, y, customer_ids, test_size=0.2, stratify=y, random_state=42
)

preprocess = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), num_cols),
        ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols),
    ]
)

model = LogisticRegression(max_iter=500, class_weight="balanced")

pipe = Pipeline(steps=[("prep", preprocess), ("model", model)])

pipe.fit(X_train, y_train)


y_pred = pipe.predict(X_test)
y_proba = pipe.predict_proba(X_test)[:, 1]

print("\nClassification report:\n", classification_report(y_test, y_pred, digits=3))
print("Confusion matrix:\n", confusion_matrix(y_test, y_pred))
print("ROC AUC:", round(roc_auc_score(y_test, y_proba), 4))


os.makedirs("outputs", exist_ok=True)
os.makedirs("models", exist_ok=True)

pred_df = pd.DataFrame(
    {
        "customerID": id_test.values,
        "churn_actual": y_test.values,
        "churn_pred": y_pred,
        "churn_proba": y_proba,
    }
)
pred_df.to_csv("outputs/churn_predictions.csv", index=False)

joblib.dump(pipe, "models/logreg_pipeline.pkl")

print("\nSaved:")
print(" - outputs/churn_predictions.csv")
print(" - models/logreg_pipeline.pkl")
