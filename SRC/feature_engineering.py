import os
import sqlite3
import pandas as pd
import numpy as np
from logger import setup_logger

logger = setup_logger()

def engineer_features(project_root):
    db_path = os.path.join(project_root, "data", "delhi_traffic.db")
    output_csv_path = os.path.join(project_root, "data", "processed", "traffic_ml_features.csv")

    logger.info("=========================================================")
    logger.info("⚡ STARTING PHASE 10: ADVANCED FEATURE ENGINEERING")
    logger.info("=========================================================")

    conn = sqlite3.connect(db_path)
    
    # Load fact data
    df = pd.read_sql("SELECT * FROM fact_traffic_monitoring_v2;", conn)
    logger.info(f"📥 Loaded {len(df):,} records for Feature Generation.")

    # -------------------------------------------------------------------------
    # 1. TIME-BASED & CYCLICAL FEATURES (Creating New Columns)
    # -------------------------------------------------------------------------
    logger.info("1️⃣ Engineering Cyclical Time Features & Day Parts...")
    
    # Hour Cyclical Encoding (Sine/Cosine transformation for ML algorithms)
    df['Hour_Sin'] = np.round(np.sin(2 * np.pi * df['Hour'] / 24.0), 4)
    df['Hour_Cos'] = np.round(np.cos(2 * np.pi * df['Hour'] / 24.0), 4)

    # Granular Day Part Categorization
    def assign_day_part(hour):
        if 5 <= hour < 12:
            return 'Morning'
        elif 12 <= hour < 17:
            return 'Afternoon'
        elif 17 <= hour < 22:
            return 'Evening'
        else:
            return 'Night'

    df['Day_Part'] = df['Hour'].apply(assign_day_part)

    # Binary Flag: Peak Congestion Window
    df['Is_Severe_Rush_Hour'] = df['Hour'].apply(lambda h: 1 if h in [8, 9, 17, 18, 19] else 0)

    # -------------------------------------------------------------------------
    # 2. VEHICLE COMPOSITION & CONGESTION RATIOS
    # -------------------------------------------------------------------------
    logger.info("2️⃣ Engineering Vehicle Ratios & Congestion Metrics...")

    # Bus-to-Car Ratio (Public vs Private Transport Load)
    df['Bus_To_Car_Ratio'] = np.round(df['Bus_Count'] / (df['Car_Count'] + 1), 4)

    # Heavy Vehicle Impact Factor (Weighted PCU share of heavy commercial vehicles)
    df['Heavy_Vehicle_PCU_Share'] = np.round(((df['Bus_Count'] * 3.0) + (df['Truck_Count'] * 3.0)) / (df['PCU_Score'] + 1e-5), 4)

    # Congestion Severity Score (Normalized against baseline benchmark)
    baseline_pcu_mean = df['PCU_Score'].mean()
    df['Congestion_Index'] = np.round(df['PCU_Score'] / baseline_pcu_mean, 2)

    # -------------------------------------------------------------------------
    # 3. TEMPORAL LAG & MOVING AVERAGE FEATURES
    # -------------------------------------------------------------------------
    logger.info("3️⃣ Generating Time-Series Lags & Moving Averages...")

    # Sort sequentially for accurate lag creation
    df = df.sort_values(by=['Date', 'Hour', 'Time_24Hr']).reset_index(drop=True)

    # 15-Minute Previous Lag PCU Score
    df['PCU_Lag_15Min'] = df.groupby('Date')['PCU_Score'].shift(1).fillna(df['PCU_Score'])

    # 1-Hour Rolling Window Average PCU
    df['PCU_Rolling_1Hr_Avg'] = np.round(
        df.groupby('Date')['PCU_Score'].transform(lambda x: x.rolling(window=4, min_periods=1).mean()), 2
    )

    # -------------------------------------------------------------------------
    # 4. SAVE FEATURE MATRIX TO DB & PROCESSED CSV
    # -------------------------------------------------------------------------
    logger.info("4️⃣ Ingesting Feature-Engineered Dataset into DB & CSV...")
    
    # Save to SQLite
    df.to_sql("fact_traffic_ml_features", conn, if_exists="replace", index=False)
    
    # Save to Processed CSV
    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
    df.to_csv(output_csv_path, index=False)
    logger.info(f"✅ Saved ML Feature Matrix ({len(df.columns)} Columns) -> {output_csv_path}")

    conn.close()

    logger.info("\n📋 NEW ENGINEERED COLUMNS AUDIT:")
    new_cols = ['Hour_Sin', 'Hour_Cos', 'Day_Part', 'Bus_To_Car_Ratio', 'Heavy_Vehicle_PCU_Share', 'Congestion_Index', 'PCU_Lag_15Min', 'PCU_Rolling_1Hr_Avg']
    print(df[new_cols].head(5).to_string(index=False))

    logger.info("\n=========================================================")
    logger.info("🎉 ADVANCED FEATURE ENGINEERING COMPLETED SUCCESSFULLY!")
    logger.info("=========================================================")

if __name__ == "__main__":
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
    engineer_features(PROJECT_ROOT)