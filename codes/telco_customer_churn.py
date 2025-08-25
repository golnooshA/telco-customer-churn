import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def print_section(title):
    bar = "—" * len(title)
    print(f"\n{title}\n{bar}")

def to_percent_table(ct):
    counts = pd.crosstab(ct.index, ct.columns).sum(axis=1) if isinstance(ct, pd.DataFrame) else None
    pct = (ct * 100).round(1)
    pct.columns = [f"Stayed % (0)" if c == 0 else f"Churned % (1)" for c in pct.columns]
    return pct

# ---------- load & clean ----------
df = pd.read_csv("data/telco_customer_churn.csv")

df['TotalCharges'] = pd.to_numeric(df['TotalCharges'].astype(str).str.strip(), errors='coerce')
df.loc[df['TotalCharges'].isna() & (df['tenure'] == 0), 'TotalCharges'] = 0
df['TotalCharges'] = df['TotalCharges'].fillna(df['TotalCharges'].median())

df['Churn'] = df['Churn'].map({'No': 0, 'Yes': 1})
y = df['Churn']

# ---------- overall churn ----------
print_section("Overall Churn Rate")
churn_rate = y.mean()
print(f"{churn_rate:.2%}")

y.value_counts(normalize=True).mul(100).plot.bar(color=["skyblue", "salmon"])
plt.title(f"Churn Rate: {churn_rate:.1%}")
plt.ylabel("Percentage (%)")
plt.xticks(ticks=[0,1], labels=["Stayed (0)", "Churned (1)"], rotation=0)
plt.tight_layout()
plt.show()

# ---------- crosstabs ----------
os.makedirs("outputs", exist_ok=True)

def build_and_print(label_col, label_name):
   
    ct_counts = pd.crosstab(df[label_col], y)                       
    ct_norm = pd.crosstab(df[label_col], y, normalize='index')      
   
    pct = (ct_norm * 100).round(1)
    pct.columns = ["Stayed % (0)", "Churned % (1)"]
    pct.insert(0, "n", ct_counts.sum(axis=1))

    print_section(f"Churn Rate by {label_name}")
    print(pct.to_string())

    ct_norm.to_csv(f"outputs/churn_by_{label_col}_proportions.csv")
    pct.to_csv(f"outputs/churn_by_{label_col}_pretty.csv", index=True)

build_and_print("Contract", "Contract Type")
build_and_print("gender", "Gender")
build_and_print("InternetService", "Internet Service")

