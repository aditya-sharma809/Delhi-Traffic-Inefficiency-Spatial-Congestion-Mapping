import os
import pandas as pd
import numpy as np

# Load Data
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "Traffic_project.csv")

if not os.path.exists(DATA_PATH):
    # Fallback search
    DATA_PATH = os.path.join(PROJECT_ROOT, "Traffic_project.csv")

df = pd.read_csv(DATA_PATH)

print("=================================================================")
print("🔍 PHASE 2: DATA UNDERSTANDING & EXPLORATORY AUDIT REPORT")
print("=================================================================\n")

# 1. Dimension & Shape Inspection
print(f"📐 1. DATASET DIMENSIONS:")
print(f"   • Total Rows (Observations): {df.shape[0]:,}")
print(f"   • Total Columns (Attributes): {df.shape[1]}")
print(f"   • Memory Usage: {df.memory_usage().sum() / 1024:.2f} KB\n")

# 2. Schema & Data Types Inspection
print("📋 2. ATTRIBUTE SCHEMA & DATA TYPES:")
print(df.dtypes.to_string())
print("\n")

# 3. Data Integrity & Completeness Audit
print("🧹 3. DATA INTEGRITY & MISSING VALUE AUDIT:")
null_counts = df.isnull().sum()
duplicate_rows = df.duplicated().sum()
print(f"   • Missing / Null Values: {null_counts.sum()}")
print(f"   • Duplicate Records: {duplicate_rows}")
print(f"   • Data Completeness Score: {((len(df) - null_counts.sum()) / len(df)) * 100:.2f}%\n")

# 4. Statistical Summary (Numerical Attributes)
print("📈 4. NUMERICAL DESCRIPTIVE STATISTICS:")
print(df.describe().T[['mean', 'std', 'min', '50%', 'max']])
print("\n")

# 5. Categorical Distribution Audit
print("🏷️ 5. CATEGORICAL ATTRIBUTE DISTRIBUTION:")
print("   • Traffic Situation Categories:")
print(df['Traffic Situation'].value_counts(normalize=True).map('{:.2%}'.format).to_string())
print("\n   • Days of Week Distribution:")
print(df['Day of the week'].value_counts().to_string())
print("\n")

# 6. Domain Consistency Verification
# Verify if Total == CarCount + BikeCount + BusCount + TruckCount
df['Calculated_Total'] = df['CarCount'] + df['BikeCount'] + df['BusCount'] + df['TruckCount']
mismatches = (df['Calculated_Total'] != df['Total']).sum()

print("⚡ 6. DOMAIN BUSINESS LOGIC AUDIT:")
print(f"   • Mismatches in Total Vehicle Sum Verification: {mismatches}")
if mismatches == 0:
    print("   ✅ Business Logic Passed: 'Total' column perfectly equals sum of all vehicle types.")
else:
    print(f"   ⚠️ Warning: Found {mismatches} mathematical discrepancies in total vehicle counts.")

print("\n=================================================================")
print("✅ DATA UNDERSTANDING AUDIT COMPLETED SUCCESSFULLY!")
print("=================================================================")